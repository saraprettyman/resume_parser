import argparse
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from pyfiglet import Figlet

from extractors.summary_extractor import SummaryExtractor
from extractors.contact_extractor import ContactExtractor
from extractors.experience_extractor import ExperienceExtractor
from extractors.education_extractor import EducationExtractor
from resume_parser.utils.skills_checker import SkillsChecker
from resume_parser.utils.display import Display

# Console renderer and display helper
console = Console()
display = Display()

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".html", ".htm"
}


def parse_args():
    parser = argparse.ArgumentParser(description="Resume Lens CLI")
    parser.add_argument("--mode", choices=["profile", "skills"], help="Mode to run")
    parser.add_argument("--sub-mode", choices=["general", "role"], help="Skills sub-mode")
    parser.add_argument("--file", help="Path to resume file")
    return parser.parse_args()


def prompt(question: str, default: str = None) -> str:
    q_text = Text(question, style="bold cyan")
    if default:
        q_text.append(f" ({default})", style="dim")
    console.print(q_text, end=" ")
    return input().strip() or default


def print_section_title(title: str) -> None:
    panel = Panel(
        Align.center(f"[bold white]{title}[/bold white]", vertical="middle"),
        style="bold blue",
        padding=(0, 2),
        expand=True
    )
    console.print(panel)


def run_cli(mode_choice: str, sub_mode: str, file_path: str):
    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix.lower()

    # Validation
    if not file_path_obj.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        return
    if ext not in SUPPORTED_EXTENSIONS:
        console.print(
            f"[red]Error:[/red] Unsupported file type: '{ext}'.\n"
            f"Please use one of: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
        return

    # Instantiate extractors and utilities
    summary_ex = SummaryExtractor()
    contact_ex = ContactExtractor()
    exp_ex = ExperienceExtractor()
    edu_ex = EducationExtractor()
    skills_checker = SkillsChecker()

    # Mode: ATS Profile Check
    if mode_choice == "profile":
        console.clear()
        print_section_title("ATS Profile Check")

        summary_res = summary_ex.extract(file_path)
        display.display_section_text("Professional Summary", summary_res.get("section", ""))

        contact_res = contact_ex.extract(file_path)
        display.display_contact(contact_res)

        console.print("\n")
        print_section_title("Education & Work Experience Check")

        edu_res = edu_ex.extract(file_path)
        exp_res = exp_ex.extract(file_path)

        display.display_education(edu_res, show_gpa=True)
        display.display_experience(exp_res)

    # Mode: Skills Analysis
    elif mode_choice == "skills":
        if sub_mode == "general":
            console.clear()
            print_section_title("General Skills Review")
            extracted = skills_checker.extract_general_skills(file_path)
            display.display_skills_table(extracted, title="")

        elif sub_mode == "role":
            console.clear()
            roles = skills_checker.load_roles()
            if not roles:
                console.print("[red]No roles found in skills_master.json[/red]")
                return

            print_section_title("Available Roles")
            for i, role in enumerate(roles, 1):
                console.print(f"[cyan]{i}[/cyan]. {role}")

            role_idx_str = prompt("Select role by number")
            if not role_idx_str:
                console.print("[red]No role selected[/red]")
                return
            try:
                role_idx = int(role_idx_str)
                role_name = roles[role_idx - 1]
            except (ValueError, IndexError):
                console.print("[red]Invalid role selection[/red]")
                return

            console.print("\n")
            print_section_title(f"Role-Specific Skills Review: {role_name}")
            extracted = skills_checker.extract_role_skills(file_path, role_name)
            display.display_skills_table(extracted)


def interactive_cli():
    console.clear()
    fig = Figlet(font="standard")
    console.print(Align.center(fig.renderText("Resume Lens")), style="bold green")
    console.print("\n")

    console.print("[bold cyan]Select an option:[/bold cyan]")
    console.print(" [green]1[/green]. Profile / Readability Check")
    console.print(" [green]2[/green]. Skills Analysis")

    mode_choice = prompt("Enter choice", "1").lower()
    mode_choice = "profile" if mode_choice in {"1", "r", "readability", "profile"} else "skills"

    sub_mode = None
    if mode_choice == "skills":
        console.print("\n[bold cyan]Select skills analysis mode:[/bold cyan]")
        console.print(" [green]g[/green]. General")
        console.print(" [green]r[/green]. Role-specific\n")
        sub_mode_choice = prompt("Enter choice", "g").lower()
        sub_mode = "general" if sub_mode_choice in {"g", "general"} else "role"

    file_path = prompt("Enter path to resume file", "real_resume_example.pdf")
    run_cli(mode_choice, sub_mode, file_path)


def main():
    args = parse_args()
    if args.mode and args.file:
        run_cli(args.mode, args.sub_mode, args.file)
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
