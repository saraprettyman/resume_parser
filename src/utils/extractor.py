import re
from rich.table import Table
from rich.console import Console
from .file_reader import read_resume
from .skills_loader import load_skills
import spacy

console = Console()

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    console.print(
        "[red][ERROR][/red] spaCy model not found. Run: [yellow]python -m spacy download en_core_web_sm[/yellow]"
    )
    raise SystemExit


class ResumeSkillExtractor:
    def __init__(self):
        self.skills_data = load_skills()

    def extract_minimal_requirements(self, file_path):
        """Check if resume has minimal ATS-readable info and return matched values."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()

        def find(pattern, text, flags=0):
            match = re.search(pattern, text, flags)
            return match.group(0) if match else None

        results = {
            "Name": find(r"[A-Z][a-z]+(?: [A-Z][a-z]+)+", resume_text),
            "Phone Number": find(r"(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}", resume_text),
            "Email": find(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", resume_lower),
            "Education": find(r"bachelor|master|phd|associate|degree|diploma", resume_lower),
            "LinkedIn": find(r"linkedin\.com\/in\/[a-z0-9\-]+", resume_lower),
            "GitHub": find(r"github\.com\/[a-z0-9\-]+", resume_lower),
            "Citizenship / Work Authorization": find(
                r"u\.?s\.?\s*citizen|united states citizen|canadian citizen|permanent resident|green card holder|work authorization",
                resume_lower
            ),
            "Work Experience": find(
                r"experience|employment history|professional history|work history", resume_lower
            )
        }

        return results

    def extract_general_skills(self, file_path):
        """Extract skills from resume without role filtering."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted = {}

        for category, skills in self.skills_data["ALL_TECHNICAL_SKILLS"].items():
            found, missing = self._match_skills(skills, resume_lower)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path, role):
        """Extract skills based on a role's required skill categories, and score ATS match %."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        role_categories = self.skills_data["ROLES"].get(role, [])
        extracted = {}
        total_skills, matched_skills = 0, 0

        for category in role_categories:
            skills = self.skills_data["ALL_TECHNICAL_SKILLS"].get(category, [])
            total_skills += len(skills)
            found, missing = self._match_skills(skills, resume_lower)
            matched_skills += len(found)
            extracted[category] = {"found": found, "missing": missing}

        score = round((matched_skills / total_skills) * 100, 2) if total_skills else 0
        return extracted, score

    def _match_skills(self, skills, resume_lower):
        """Match skills from skills_master.json against resume."""
        found, missing = [], []
        for skill in skills:
            skill_names = [skill["name"].lower()] + [alias.lower() for alias in skill["aliases"]]
            matched = any(re.search(rf"\b{s}\b", resume_lower) for s in skill_names)
            if matched:
                found.append(skill["name"])
            else:
                missing.append(skill["name"])
        return found, missing

    def display_combined_table(self, extracted, title, score=None):
        """Display found/missing skills in a combined category table with colors."""
        table = Table(title=f"[bold bright_cyan]{title}[/bold bright_cyan]", show_lines=True)
        table.add_column("Category", style="bold yellow", no_wrap=True)
        table.add_column("Skills", style="white")

        for category, data in extracted.items():
            found_sorted = sorted(data["found"], key=lambda s: s.lower())
            missing_sorted = sorted(data["missing"], key=lambda s: s.lower())

            found_str = ", ".join(f"[bold bright_green]{s}[/bold bright_green]" for s in found_sorted) \
                if found_sorted else "[dim]None[/dim]"

            missing_str = ", ".join(f"[dim red]{s}[/dim red]" for s in missing_sorted) if missing_sorted else ""

            combined_str = found_str
            if missing_str:
                combined_str += f"  |  {missing_str}"

            table.add_row(category, combined_str)

        console.print(table)
        if score is not None:
            console.print(
                f"[bold yellow]ATS Compatibility Score:[/bold yellow] [bold bright_white]{score}%[/bold bright_white]"
            )
