# interfaces/cli/main.py
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import asyncio

from core import ModelType, ModelManager, LLMClient
from config.settings import settings

app = typer.Typer(help="LLM API Interface CLI")
console = Console()

@app.command()
def list_models():
    """List available models and their capabilities"""
    table = Table(show_lines=True)
    table.add_column("Model", width=30)
    table.add_column("Max Tokens", justify="right")
    table.add_column("Context Window", justify="right")
    table.add_column("Capabilities", width=40)
    
    manager = ModelManager()
    for model_type in ModelType:
        config = manager.get_model_config(model_type)
        table.add_row(
            model_type.value,
            str(config.max_tokens),
            str(config.context_window),
            ", ".join(config.capabilities)
        )
    
    console.print(table)

@app.command()
def chat(
    model: str = typer.Option("gpt-4o", help="Model to use"),
    max_tokens: Optional[int] = typer.Option(None, help="Max tokens in response"),
    temperature: float = typer.Option(0.7, help="Temperature for sampling"),
):
    """Start an interactive chat session"""
    try:
        model_type = ModelType(model)
    except ValueError:
        console.print(f"[red]Invalid model: {model}[/red]")
        console.print("Available models:")
        list_models()
        return

    async def chat_session():
        async with LLMClient() as client:
            console.print("[green]Starting chat session (Ctrl+C to exit)[/green]")
            while True:
                try:
                    prompt = typer.prompt("\nYou")
                    messages = [{"role": "user", "content": prompt}]
                    
                    with console.status("[bold green]Thinking..."):
                        response = await client.generate(
                            model_type=model_type,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                    
                    assistant_response = client.extract_response(model_type, response)
                    console.print(f"\n[blue]Assistant:[/blue] {assistant_response}")
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Ending chat session[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
                    break

    asyncio.run(chat_session())

@app.command()
def cost_estimate(
    model: str = typer.Option(..., "--model", "-m", help="Model name"),
    input_tokens: int = typer.Option(..., "--input", "-i", help="Number of input tokens"),
    output_tokens: int = typer.Option(..., "--output", "-o", help="Expected number of output tokens"),
):
    """Estimate cost for a model run"""
    try:
        model_type = ModelType(model)
        manager = ModelManager()
        cost = manager.calculate_cost(model_type, input_tokens, output_tokens)
        console.print(f"Estimated cost: ${cost:.4f}")
    except ValueError:
        console.print(f"[red]Invalid model: {model}[/red]")
        console.print("Available models:")
        list_models()
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()