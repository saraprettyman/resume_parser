# cli.py
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from pyfiglet import Figlet
from pathlib import Path

from extractors.summary_extractor import SummaryExtractor
from extractors.contact_extractor import ContactExtractor
from extractors.experience_extractor import ExperienceExtractor
from extractors.education_extractor import EducationExtractor
from skills_checker.skills_checker import SkillsChecker
from utils.display import Display

console = Console()
display = Display()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".html", ".htm"}

def prompt(question, default=None):
    q_text = Text(question, style="bold cyan")
    if default:
        q_text.append(f" ({default})", style="dim")
    console.print(q_text, end=" ")
    return input().strip() or default

def print_section_title(title):
    panel = Panel(
        Align.center(f"[bold white]{title}[/bold white]", vertical="middle"),
        style="bold blue",
        padding=(0, 2),
        expand=True
    )
    console.print(panel)
def interactive_cli():
    console.clear()

    # Show banner
    fig = Figlet(font="standard")
    console.print(Align.center(fig.renderText("Resume Lens")), style="bold green")
    console.print("\n")
    console.print(Panel(
        Align.center(
            "[bold cyan]Welcome to Resume Lens![/bold cyan]\n\n"
            "Analyze resumes for ATS compatibility, skills matching,\n"
            "and overall profile readiness.\n",
            vertical="middle"
        ),
        style="bold blue",
        padding=(0, 0)
    ))

    # Ask for mode first
    console.print("\n[bold yellow]Please choose an analysis mode:[/bold yellow]")
    console.print("[cyan]1.[/cyan] Profile / Readability (ATS Profile Check)")
    console.print("[cyan]2.[/cyan] Skills Analysis\n")

    mode_choice = input("Enter choice (1 or 2) [default: 2]: ").strip() or "2"
    if mode_choice == "1":
        mode_choice = "r"
    elif mode_choice == "2":
        mode_choice = "s"
    else:
        console.print("[red]Invalid choice. Defaulting to Skills Analysis.[/red]")
        mode_choice = "s"

    # Now ask for the file
    console.print("\n")
    file_path = prompt("Enter path to resume file", "real_resume_example.pdf")
    console.print("\n")

    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix.lower()

    if not file_path_obj.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        return
    if ext not in SUPPORTED_EXTENSIONS:
        console.print(
            f"[red]Error:[/red] Unsupported file type: '{ext}'.\n"
            f"Please use one of the following: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
        return

    # Instantiate extractors/checkers
    summary_ex = SummaryExtractor()
    contact_ex = ContactExtractor()
    exp_ex = ExperienceExtractor()
    edu_ex = EducationExtractor()
    skills_checker = SkillsChecker()

    console.print("\n")

    if mode_choice in ["r", "readability", "profile"]:
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

        # TODO: add a project section

    elif mode_choice in ["s", "skills"]:
        sub_mode = prompt("Choose skills analysis mode [g: general, r: role]", "g").lower()
        console.print("\n")

        if sub_mode in ["g", "general"]:
            print_section_title("General Skills Review")
            extracted = skills_checker.extract_general_skills(file_path)
            display.display_skills_table(extracted, title="")

        elif sub_mode in ["r", "role"]:
            roles = skills_checker.load_roles()
            if not roles:
                console.print("[red]No roles found in skills_master.json[/red]")
                return

            print_section_title("Available Roles")
            for i, role in enumerate(roles, 1):
                console.print(f"[cyan]{i}[/cyan]. {role}")

            role_idx_str = prompt("Select role by number")
            if role_idx_str is None:
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
