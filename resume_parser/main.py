from cli import interactive_cli
import sys
from rich.console import Console

console = Console()

if __name__ == "__main__":
    try:
        interactive_cli()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exited by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
