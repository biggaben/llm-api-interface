# app.py
import asyncio
import typer
from rich import print
from interfaces.cli.main import app as cli_app
from config.settings import settings
from core import LLMClient, ModelType

async def test_connection():
    """Test API connections"""
    try:
        async with LLMClient() as client:
            # Test Claude connection
            claude_response = await client.generate(
                model_type=ModelType.CLAUDE,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            print(f"[green]✓[/green] Claude API connection successful: {client.extract_response(ModelType.CLAUDE, claude_response)}")

            # Test OpenAI connection
            openai_response = await client.generate(
                model_type=ModelType.GPT4O,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            print(f"[green]✓[/green] OpenAI API connection successful: {client.extract_response(ModelType.GPT4O, openai_response)}")

    except Exception as e:
        print(f"[red]✗[/red] API connection failed: {str(e)}")
        raise typer.Exit(code=1)

def main():
    """Main application entry point"""
    # Verify environment
    if not settings.ANTHROPIC_API_KEY or not settings.OPENAI_API_KEY:
        print("[red]Error:[/red] API keys not found in environment")
        print("Please set ANTHROPIC_API_KEY and OPENAI_API_KEY")
        raise typer.Exit(code=1)

    # Test connections
    print("Testing API connections...")
    asyncio.run(test_connection())
    
    # Launch CLI
    cli_app()

if __name__ == "__main__":
    main()