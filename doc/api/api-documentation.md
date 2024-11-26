# API Documentation

## Core Components

### ModelManager

The ModelManager handles model selection and usage tracking.

```python
from core import ModelManager, ModelType

manager = ModelManager()

# Select appropriate model
model = await manager.select_model(
    task_type="analysis",
    input_length=1000,
    priority="balanced",
    budget=0.05
)

# Calculate costs
cost = manager.calculate_cost(
    model=ModelType.CLAUDE,
    input_tokens=1000,
    output_tokens=500
)

# Get usage metrics
metrics = manager.get_metrics()
```

### LLMClient

The LLMClient handles direct interactions with LLM APIs.

```python
from core import LLMClient, ModelType

async with LLMClient() as client:
    # Basic generation
    response = await client.generate(
        model_type=ModelType.GPT4O,
        messages=[{"role": "user", "content": "Hello!"}],
        max_tokens=100
    )
    
    # Streaming response
    async for chunk in client.stream_response(response):
        print(chunk, end="")
```

## Model Types

```python
from core import ModelType

# Available models
ModelType.CLAUDE      # "claude-3-5-sonnet-20241022"
ModelType.GPT4O      # "gpt-4o"
ModelType.O1_PREVIEW # "o1-preview"
```

## Cache System

```python
from utils.cache import CacheManager

cache = CacheManager()

# Get cached response
response = cache.get(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# Cache response
cache.set(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    response={"choices": [{"message": {"content": "Hi!"}}]}
)

# Clear old cache entries
cache.clear(age_hours=24)
```

## Settings Management

```python
from config.settings import settings

# Access settings
api_timeout = settings.API_TIMEOUT
cache_enabled = settings.CACHE_ENABLED

# Override settings
settings.CACHE_TTL = 7200  # 2 hours
settings.LOG_LEVEL = "DEBUG"
```

## Error Handling

```python
from core import APIError, RateLimitError, TokenLimitError

try:
    async with LLMClient() as client:
        response = await client.generate(...)
except RateLimitError:
    # Handle rate limiting
    pass
except TokenLimitError:
    # Handle token limit exceeded
    pass
except APIError as e:
    # Handle other API errors
    print(f"API Error: {str(e)}")
```

## CLI Commands

### List Models

```bash
llm-cli list-models
```

### Chat Session

```bash
llm-cli chat --model gpt-4o --temperature 0.7
```

### Cost Estimation

```bash
llm-cli cost-estimate \
    --model claude-3-5-sonnet-20241022 \
    --input-tokens 1000 \
    --output-tokens 500
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Optional
DEBUG=False
API_TIMEOUT=30
CACHE_ENABLED=True
LOG_LEVEL=INFO
```

## Best Practices

1. **Resource Management**:
   - Always use async context managers
   - Close clients properly
   - Clear cache periodically

2. **Error Handling**:
   - Catch specific exceptions
   - Implement retries for transient errors
   - Log errors appropriately

3. **Performance**:
   - Use streaming for long responses
   - Implement caching for repeated requests
   - Monitor token usage

4. **Security**:
   - Never hardcode API keys
   - Use environment variables
   - Implement rate limiting

5. **Testing**:
   - Write unit tests for new features
   - Use mocks for API calls
   - Test error conditions
