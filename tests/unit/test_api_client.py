# tests/unit/test_api_client.py
import pytest
import aiohttp
from unittest.mock import Mock, patch
from core.api.client import LLMClient, APIError, RateLimitError, TokenLimitError
from core.models.config import ModelType

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_response():
    class MockResponse:
        def __init__(self, status=200, json_data=None):
            self._status = status
            self._json_data = json_data or {}

        @property
        def status(self):
            return self._status

        async def json(self):
            return self._json_data

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def close(self):
            pass

    return MockResponse

@pytest.fixture
def mock_streaming_response():
    class MockStreamingResponse:
        def __init__(self):
            self.content = Mock()
            async def async_iter():
                for line in [
                    b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
                    b'data: {"choices":[{"delta":{"content":" World"}}]}',
                    b'data: [DONE]'
                ]:
                    yield line
            
            self.content.iter_lines = async_iter
            self.status = 200
            
        def close(self):
            pass
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.close()
            
        async def json(self):
            return {"choices": [{"delta": {"content": "Hello World"}}]}

    return MockStreamingResponse

class TestLLMClient:
    async def test_client_initialization(self):
        async with LLMClient() as client:
            assert client._session is not None
            assert isinstance(client._session, aiohttp.ClientSession)

    async def test_headers_formation(self):
        client = LLMClient()
        
        claude_headers = client._get_headers(ModelType.CLAUDE)
        assert "x-api-key" in claude_headers
        assert "anthropic-version" in claude_headers
        
        gpt_headers = client._get_headers(ModelType.GPT4O)
        assert "Authorization" in gpt_headers
        assert gpt_headers["Authorization"].startswith("Bearer ")

    async def test_url_formation(self):
        client = LLMClient()
        
        claude_url = client._get_api_url(ModelType.CLAUDE)
        assert "anthropic" in claude_url
        
        openai_url = client._get_api_url(ModelType.GPT4O)
        assert "openai" in openai_url
        
        o1_url = client._get_api_url(ModelType.O1_PREVIEW)
        assert "openai" in o1_url

    @pytest.mark.parametrize("model_type,expected_response", [
        (ModelType.CLAUDE, "This is a test response"),
        (ModelType.GPT4O, "This is a test response"),
        (ModelType.O1_PREVIEW, "This is a test response"),
    ])
    async def test_generate_success(self, mock_response, model_type, expected_response):
        response_data = {
            ModelType.CLAUDE: {
                "content": [{"text": expected_response}]
            },
            ModelType.GPT4O: {
                "choices": [{"message": {"content": expected_response}}]
            },
            ModelType.O1_PREVIEW: {
                "choices": [{"message": {"content": expected_response}}]
            }
        }[model_type]

        mock_resp = mock_response(json_data=response_data)
        
        async with LLMClient() as client:
            with patch.object(client._session, 'post', return_value=mock_resp):
                response = await client.generate(
                    model_type=model_type,
                    messages=[{"role": "user", "content": "test"}]
                )
                assert client.extract_response(model_type, response) == expected_response

    @pytest.mark.parametrize("error_status,expected_exception", [
        (429, RateLimitError),
        (400, APIError),
        (500, APIError),
    ])
    async def test_error_handling(self, mock_response, error_status, expected_exception):
        mock_resp = mock_response(status=error_status, json_data={"error": {"message": "error"}})
        
        async with LLMClient() as client:
            with patch.object(client._session, 'post', return_value=mock_resp):
                with pytest.raises(expected_exception):
                    await client.generate(
                        model_type=ModelType.CLAUDE,
                        messages=[{"role": "user", "content": "test"}]
                    )

    async def test_token_limit_error(self, mock_response):
        error_response = {
            "error": {
                "message": "Maximum token limit exceeded"
            }
        }
        mock_resp = mock_response(status=400, json_data=error_response)
        
        async with LLMClient() as client:
            with patch.object(client._session, 'post', return_value=mock_resp):
                with pytest.raises(TokenLimitError):
                    await client.generate(
                        model_type=ModelType.GPT4O,
                        messages=[{"role": "user", "content": "test"}]
                    )

    async def test_streaming_response(self, mock_streaming_response):
        mock_resp = mock_streaming_response()
        
        async with LLMClient() as client:
            with patch.object(client._session, 'post', return_value=mock_resp):
                response = await client.generate(
                    model_type=ModelType.GPT4O,
                    messages=[{"role": "user", "content": "test"}],
                    stream=True
                )
                chunks = []
                async for chunk in client.stream_response(response):
                    chunks.append(chunk)
                
                assert chunks == ["Hello", " World"]

    async def test_model_config_validation(self):
        client = LLMClient()
        
        for model_type in ModelType:
            headers = client._get_headers(model_type)
            assert isinstance(headers, dict)
            assert "content-type" in headers
            
            url = client._get_api_url(model_type)
            assert isinstance(url, str)
            assert url.startswith("https://")