# LLM API Interface

A robust Python interface for managing multiple LLM APIs with intelligent model selection, caching, and usage tracking.

## Features

- **Multiple Model Support**:
  - Claude-3-5-sonnet
  - GPT-4o
  - o1-preview

- **Intelligent Model Selection**:
  - Task-based routing
  - Budget constraints
  - Context length optimization
  - Performance requirements

- **Advanced Features**:
  - Async/await design
  - Response streaming
  - Request caching
  - Cost tracking
  - Usage analytics
  - Rate limiting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-api-interface.git
cd llm-api-interface
```

2. Set up conda environment:
```bash
conda env create -f environment.yml
conda activate llm-api-interface
```

3. Install package:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
# Create .env file with your API keys
echo "ANTHROPIC_API_KEY=your_anthropic_key" > .env
echo "OPENAI_API_KEY=your_openai_key" >> .env
```

## Usage

### CLI Interface

1. List available models:
```bash
llm-cli list-models
```

2. Start chat session:
```bash
llm-cli chat --model gpt-4o
```

3. Estimate costs:
```bash
llm-cli cost-estimate --model claude-3-5-sonnet-20241022 --input-tokens 1000 --output-tokens 500
```

### Python API

```python
import asyncio
from core import LLMClient, ModelType, ModelManager

async def main():
    # Initialize client
    async with LLMClient() as client:
        # Generate response
        response = await client.generate(
            model_type=ModelType.GPT4O,
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=100
        )
        print(client.extract_response(ModelType.GPT4O, response))

    # Use model manager for intelligent selection
    manager = ModelManager()
    model = await manager.select_model(
        task_type="analysis",
        input_length=5000,
        budget=0.1
    )
    print(f"Recommended model: {model}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

Configuration is managed through `config/settings.py` and environment variables:

```python
# Available settings
DEBUG=False
API_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT_PER_MINUTE=60
CACHE_ENABLED=True
CACHE_TTL=3600
LOG_LEVEL=INFO
```

## Project Structure

```
llm-api-interface/
├── core/                 # Core functionality
│   ├── models/          # Model management
│   ├── api/             # API clients
│   └── security/        # Key management
├── interfaces/          # User interfaces
│   ├── cli/            # Command line interface
│   └── gui/            # Future GUI support
├── utils/              # Utilities
│   ├── cache/          # Response caching
│   ├── docs/           # Documentation
│   └── history/        # Usage history
└── tests/              # Test suite
```

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_api_client.py

# Run with coverage
pytest --cov=core
```

## Model Selection Logic

The system intelligently selects models based on:

1. **Task Type**:
   - Complex reasoning → o1-preview
   - Code generation → GPT4O
   - Creative writing → Claude

2. **Budget**:
   - Low budget (<$0.02/1k tokens) → GPT4O
   - Medium budget → Claude
   - High budget → o1-preview

3. **Input Length**:
   - >100K tokens → Claude (large context)
   - Standard → GPT4O
   - Performance critical → o1-preview

## Cache System

Response caching is implemented with:
- TTL-based expiration
- SHA-256 request hashing
- Configurable cache location
- Automatic cleanup

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.