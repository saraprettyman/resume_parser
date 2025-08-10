from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from pyfiglet import Figlet
from pathlib import Path

from src.utils.extractor import ResumeSkillExtractor
from src.utils.extractor_profile import ProfileExtractor
from src.utils.extractor_edu_exp import ATSEducationExperienceExtractor
from src.utils.skills_loader import load_roles

console = Console()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".rtf"}

def prompt(question, default=None):
    """Stylized inline prompt with default option."""
    q_text = Text(question, style="bold cyan")
    if default:
        q_text.append(f" ({default})", style="dim")
    console.print(q_text, end=" ")
    return input().strip() or default

def print_section_title(title):
    """Centered, bold section title inside a panel."""
    panel = Panel(
        Align.center(f"[bold white]{title}[/bold white]", vertical="middle"),
        style="bold blue",
        padding=(0, 2),
        expand=True
    )
    console.print(panel)

def interactive_cli():
    console.clear()

    # Figlet banner
    fig = Figlet(font="standard")
    console.print(Align.center(fig.renderText("Resume Parser Tool")), style="bold green")
    console.print("\n")

    # File path prompt
    file_path = prompt("Enter path to resume file", "tests/real_resume.pdf")
    console.print("\n")

    # --- Early Validation ---
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
    # ------------------------

    # Mode selection (single letter)
    mode_choice = prompt("Choose analysis mode [r: profile/readability, s: skills]", "s").lower()

    extractor_skills = ResumeSkillExtractor()
    extractor_profile = ProfileExtractor()
    extractor_edu_work = ATSEducationExperienceExtractor()

    console.print("\n")

    if mode_choice in ["r", "readability", "profile"]:
        print_section_title("ATS Profile Check")
        profile_results = extractor_profile.extract_profile_info(file_path)
        extractor_profile.display_profile_table(profile_results)

        console.print("\n")
        print_section_title("Education & Work Experience Check")
        edu_work_results = extractor_edu_work.extract_edu_exp(file_path)
        extractor_edu_work.display_edu_exp_table(edu_work_results)

    elif mode_choice in ["s", "skills"]:
        sub_mode = prompt("Choose skills analysis mode [g: general, r: role]", "g").lower()

        console.print("\n")

        if sub_mode in ["g", "general"]:
            print_section_title("General Skills Review")
            extracted = extractor_skills.extract_general_skills(file_path)
            extractor_skills.display_combined_table(extracted, title="")

        elif sub_mode in ["r", "role"]:
            roles = load_roles()
            if not roles:
                console.print("[red]No roles found in skills_master.json[/red]")
                return

            print_section_title("Available Roles")
            for i, role in enumerate(roles, 1):
                console.print(f"[cyan]{i}[/cyan]. {role}")

            role_idx_str = prompt("Select role by number")
            try:
                role_idx = int(role_idx_str)
                role_name = roles[role_idx - 1]
            except (ValueError, IndexError):
                console.print("[red]Invalid role selection[/red]")
                return
            
            console.print("\n")
            print_section_title(f"Role-Specific Skills Review: {role_name}")
            extracted, score = extractor_skills.extract_role_skills(file_path, role_name)
            extractor_skills.display_combined_table(
                extracted, score=score
            )

    else:
        console.print("[red]Invalid analysis mode[/red]")

if __name__ == "__main__":
    interactive_cli()
