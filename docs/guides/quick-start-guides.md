# Quick Start Guides

## 1. Interactive Chat

Create a simple chat application:

```python
import asyncio
from core import LLMClient, ModelType
from rich import print

async def chat():
    async with LLMClient() as client:
        print("[bold green]Chat started (Ctrl+C to exit)[/bold green]")
        
        while True:
            try:
                user_input = input("\nYou: ")
                response = await client.generate(
                    model_type=ModelType.GPT4O,
                    messages=[{"role": "user", "content": user_input}]
                )
                assistant_response = client.extract_response(ModelType.GPT4O, response)
                print(f"\n[bold blue]Assistant:[/bold blue] {assistant_response}")
            
            except KeyboardInterrupt:
                print("\n[yellow]Chat ended[/yellow]")
                break

if __name__ == "__main__":
    asyncio.run(chat())
```

## 2. Streaming Responses

Stream long-form content:

```python
import asyncio
from core import LLMClient, ModelType

async def stream_response():
    async with LLMClient() as client:
        response = await client.generate(
            model_type=ModelType.CLAUDE,
            messages=[{
                "role": "user",
                "content": "Write a long story about..."
            }],
            stream=True
        )
        
        async for chunk in client.stream_response(response):
            print(chunk, end="", flush=True)

asyncio.run(stream_response())
```

## 3. Cost-Effective Usage

Implement budget-aware processing:

```python
from core import ModelManager

async def process_with_budget(text: str, max_budget: float):
    manager = ModelManager()
    
    # Select model based on budget
    model = await manager.select_model(
        task_type="analysis",
        input_length=len(text),
        budget=max_budget
    )
    
    # Calculate estimated cost
    estimated_cost = manager.calculate_cost(
        model=model,
        input_tokens=len(text) // 4,  # rough estimation
        output_tokens=100
    )
    
    if estimated_cost > max_budget:
        raise ValueError("Budget too low for task")
    
    # Process text
    async with LLMClient() as client:
        response = await client.generate(
            model_type=model,
            messages=[{"role": "user", "content": text}]
        )
        return client.extract_response(model, response)
```

## 4. Caching Responses

Implement caching for repeated queries:

```python
from utils.cache import CacheManager
from core import LLMClient, ModelType

async def cached_query(prompt: str):
    cache = CacheManager()
    model = ModelType.GPT4O
    messages = [{"role": "user", "content": prompt}]
    
    # Check cache first
    if cached := cache.get(model.value, messages):
        return cached
    
    # Generate new response if not cached
    async with LLMClient() as client:
        response = await client.generate(
            model_type=model,
            messages=messages
        )
        
        # Cache the response
        cache.set(model.value, messages, response)
        return response
```

## 5. Error Handling

Implement robust error handling:

```python
from core import LLMClient, ModelType, APIError, RateLimitError
import asyncio
import logging

async def robust_generation(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async with LLMClient() as client:
                response = await client.generate(
                    model_type=ModelType.GPT4O,
                    messages=[{"role": "user", "content": prompt}]
                )
                return client.extract_response(ModelType.GPT4O, response)
                
        except RateLimitError:
            wait_time = (attempt + 1) * 5  # Exponential backoff
            logging.warning(f"Rate limit hit, waiting {wait_time}s...")
            await asyncio.sleep(wait_time)
            
        except APIError as e:
            logging.error(f"API Error: {str(e)}")
            if attempt == max_retries - 1:
                raise
            
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise
            
    raise RuntimeError("Max retries exceeded")
```
