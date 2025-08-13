"""Entry point for the Resume Parser interactive CLI."""

import sys
from rich.console import Console
from resume_parser.cli import interactive_cli  # adjust import path if needed

console = Console()

if __name__ == "__main__":
    try:
        interactive_cli()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exited by user.[/bold yellow]")
        sys.exit(0)
    except (OSError, ValueError, RuntimeError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
