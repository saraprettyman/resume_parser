from rich.console import Console
from rich.text import Text
from rich.table import Table
from pyfiglet import Figlet
from src.utils.extractor import ResumeSkillExtractor
from src.utils.skills_loader import load_roles

console = Console()

def prompt(question, default=None):
    q_text = Text(question, style="bold cyan")
    if default:
        q_text.append(f" ({default})", style="dim")
    console.print(q_text, end=" ")
    return input().strip() or default

def interactive_cli():
    extractor = ResumeSkillExtractor()

    console.print(Figlet(font="slant").renderText("Resume Analyzer"), style="bold bright_cyan")
    console.rule("[bold cyan]Resume Skills & ATS Tool[/bold cyan]")

    file_path = prompt("Enter path to resume file", "tests/sample_resume.pdf")
    mode = prompt("Choose analysis mode [readability/skills]", "skills").lower()

    if mode == "readability":
        results = extractor.extract_minimal_requirements(file_path)
        console.rule("[bold cyan]ATS Readability Check[/bold cyan]")

        table = Table(show_lines=True)
        table.add_column("Category", style="bold yellow")
        table.add_column("Status", style="bold white")
        table.add_column("Extracted Value", style="white")

        for field, value in results.items():
            status = "[green]Found[/green]" if value else "[red]Missing[/red]"
            display_value = value if value else ""
            table.add_row(field, status, display_value)

        console.print(table)
        return

    elif mode == "skills":
        sub_mode = prompt("Choose skills analysis type [general/role]", "general").lower()

        if sub_mode == "general":
            extracted = extractor.extract_general_skills(file_path)
            extractor.display_combined_table(extracted, title="General Skills Review")

        elif sub_mode == "role":
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

            extracted, score = extractor.extract_role_skills(file_path, role_name)
            extractor.display_combined_table(extracted, title=f"Role-Specific Skills Review: {role_name}", score=score)
        else:
            console.print("[red]Invalid skills analysis type[/red]")

    else:
        console.print("[red]Invalid analysis mode[/red]")

if __name__ == "__main__":
    interactive_cli()
