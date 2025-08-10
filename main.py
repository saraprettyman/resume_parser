from rich.console import Console
from rich.text import Text
from src.utils.extractor import ResumeSkillExtractor
from src.utils.skills_loader import load_roles

console = Console()


def prompt(question, default=None):
    """Stylized inline prompt with default option."""
    q_text = Text(question, style="bold cyan")
    if default:
        q_text.append(f" ({default})", style="dim")
    console.print(q_text, end=" ")
    return input().strip() or default


def interactive_cli():
    extractor = ResumeSkillExtractor()

    console.rule("[bold cyan]Resume Skills Extraction Tool[/bold cyan]")

    # File path prompt
    console.print("")
    file_path = prompt("Enter path to resume file", "tests/sample_resume.pdf")

    # Mode selection
    console.print("")
    mode = prompt("Choose analysis mode [general/role]", "general").lower()

    # Verbose toggle
    console.print("")
    verbose_choice = prompt("Verbose output with context? [y/N]", "n").lower()
    verbose = verbose_choice == "y"

    console.print("\n[cyan]Reading resume...[/cyan]")

    if mode == "general":
        extracted = extractor.extract_general_skills(file_path, verbose=verbose)
        extractor.display_combined_table(extracted, title="General Skills Review")

    elif mode == "role":
        # Show available roles
        roles = load_roles()
        if not roles:
            console.print("[red]No roles found in skills_master.json[/red]")
            return

        console.print("\n[bold cyan]Available Roles:[/bold cyan]")
        for i, role in enumerate(roles, 1):
            console.print(f"{i}. {role}")

        role_idx = prompt("Select role by number")
        try:
            role_name = roles[int(role_idx) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid role selection[/red]")
            return

        extracted, score = extractor.extract_role_skills(file_path, role_name, verbose=verbose)
        extractor.display_combined_table(extracted, title=f"Role-Specific Skills Review: {role_name}", score=score)

    else:
        console.print("[red]Invalid analysis mode[/red]")


if __name__ == "__main__":
    interactive_cli()
