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

    def extract_general_skills(self, file_path):
        """Extract skills from resume without role filtering."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted = {}

        for category, skills in self.skills_data["ALL_TECHNICAL_SKILLS"].items():
            found, missing = self._match_skills(skills, resume_lower, resume_text)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path, role):
        """Extract skills for a specific role."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        role_categories = self.skills_data["ROLES"].get(role, [])
        extracted = {}
        total_skills, matched_skills = 0, 0

        for category in role_categories:
            skills = self.skills_data["ALL_TECHNICAL_SKILLS"].get(category, [])
            total_skills += len(skills)
            found, missing = self._match_skills(skills, resume_lower, resume_text)
            matched_skills += len(found)
            extracted[category] = {"found": found, "missing": missing}

        score = round((matched_skills / total_skills) * 100, 2) if total_skills else 0
        return extracted, score

    def _match_skills(self, skills, resume_lower, resume_text):
        """Match skills with aliases against resume text."""
        found, missing = [], []
        for skill in skills:
            skill_names = [skill["name"].lower()] + [alias.lower() for alias in skill.get("aliases", [])]
            matched = False
            for s in skill_names:
                if re.search(rf"\b{s}\b", resume_lower):
                    found.append(skill["name"])
                    matched = True
                    break
            if not matched:
                missing.append(skill["name"])
        return found, missing

    def display_combined_table(self, extracted, title=None, score=None):
        """Display skills in a combined found/missing format with optional title."""
        table = Table(
            title=title if title else "Skills Review",
            show_lines=True,
            expand=True
        )
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Skills", style="white")

        for category, data in extracted.items():
            found_str = ", ".join(f"[green]{s}[/green]" for s in data["found"]) if data["found"] else "[dim]None[/dim]"
            missing_str = ", ".join(f"[dim]{s}[/dim]" for s in data["missing"]) if data["missing"] else ""
            combined_str = found_str + (f"  |  {missing_str}" if missing_str else "")
            table.add_row(category, combined_str)

        console.print(table)
        if score is not None:
            console.print(f"[bold]ATS Compatibility Score:[/bold] {score}%")
