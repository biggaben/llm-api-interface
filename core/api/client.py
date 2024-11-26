# core/api/client.py
from typing import Optional, Dict, Any, List, AsyncGenerator
import aiohttp
import json
import logging
from ..models.config import ModelType
from ..security.keys import get_api_key

class APIError(Exception):
    """Base exception for API errors"""
    pass

class RateLimitError(APIError):
    """Raised when hitting rate limits"""
    pass

class TokenLimitError(APIError):
    """Raised when exceeding token limits"""
    pass

class LLMClient:
    def __init__(self):
        self.anthropic_base_url = "https://api.anthropic.com/v1/messages"
        self.openai_base_url = "https://api.openai.com/v1/chat/completions"
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    def _get_headers(self, model_type: ModelType) -> Dict[str, str]:
        """Get appropriate headers for the model type."""
        api_key = get_api_key(model_type)
        
        if model_type == ModelType.CLAUDE:
            return {
                "x-api-key": api_key,
                "anthropic-version": "2024-01-01",
                "content-type": "application/json"
            }
        return {
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json"
        }

    def _get_api_url(self, model_type: ModelType) -> str:
        """Get appropriate API URL for the model type."""
        if model_type == ModelType.CLAUDE:
            return self.anthropic_base_url
        return self.openai_base_url

    async def generate(
        self,
        model_type: ModelType,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the specified model.
        
        Args:
            model_type: The type of model to use
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
            **kwargs: Additional model-specific parameters
        
        Returns:
            API response as a dictionary
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        url = self._get_api_url(model_type)
        headers = self._get_headers(model_type)

        try:
            if model_type == ModelType.CLAUDE:
                payload = {
                    "model": model_type.value,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": stream,
                    **kwargs
                }
            else:  # OpenAI models
                payload = {
                    "model": model_type.value,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stream": stream,
                    **kwargs
                }

            self.logger.debug(f"Sending request to {model_type.value}")
            
            async with self._session.post(url, headers=headers, json=payload) as response:
                if response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status == 400:
                    error_data = await response.json()
                    if "token limit" in error_data.get("error", {}).get("message", "").lower():
                        raise TokenLimitError("Token limit exceeded")
                    raise APIError(f"API error: {error_data}")
                elif response.status != 200:
                    raise APIError(f"API returned status code: {response.status}")
                
                if stream:
                    return response  # Return the response object for streaming
                return await response.json()

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {str(e)}")
            raise APIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
            raise APIError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    @staticmethod
    def extract_response(model_type: ModelType, response: Dict[str, Any]) -> str:
        """Extract the response text from the API response."""
        if model_type == ModelType.CLAUDE:
            return response["content"][0]["text"]
        return response["choices"][0]["message"]["content"]

    async def stream_response(self, response: aiohttp.ClientResponse) -> AsyncGenerator[str, None]:
        """
        Stream the response from the API.
        
        Args:
            response: The streaming response from the API
            
        Yields:
            Chunks of the generated text
        """
        try:
            async for line in response.content.iter_lines():
                if line:
                    if line.startswith(b"data: "):
                        if line.strip() == b"data: [DONE]":
                            break
                        chunk = json.loads(line.removeprefix(b"data: ").decode())
                        if chunk.get("choices") and chunk["choices"][0].get("delta"):
                            if "content" in chunk["choices"][0]["delta"]:
                                yield chunk["choices"][0]["delta"]["content"]
        finally:
            response.close()
