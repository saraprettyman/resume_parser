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

    def extract_general_skills(self, file_path, verbose=False):
        """Extract skills from resume without role filtering."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted = {}

        for category, skills in self.skills_data["ALL_TECHNICAL_SKILLS"].items():
            found, missing = self._match_skills(skills, resume_text, resume_lower, verbose)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path, role, verbose=False):
        """Extract skills based on a role's required skills, and score ATS match %."""
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        role_skills = self.skills_data["ROLES"].get(role, {})
        extracted = {}
        total_skills, matched_skills = 0, 0

        for category, skills in role_skills.items():
            total_skills += len(skills)
            found, missing = self._match_simple_skills(skills, resume_text, resume_lower, verbose)
            matched_skills += len(found)
            extracted[category] = {"found": found, "missing": missing}

        score = round((matched_skills / total_skills) * 100, 2) if total_skills else 0
        return extracted, score

    def _match_skills(self, skills, resume_text, resume_lower, verbose):
        """Match skills from skills_master.json against resume, punctuation-safe."""
        found, missing = [], []
        for skill in skills:
            skill_names = [skill["name"].lower()] + [alias.lower() for alias in skill["aliases"]]
            matched = False
            for s in skill_names:
                # Allow punctuation or parentheses before/after, not just spaces
                pattern = rf"(?<!\w){re.escape(s)}(?!\w)"
                match = re.search(pattern, resume_lower, flags=re.MULTILINE)
                if match:
                    if verbose:
                        context = resume_text[max(0, match.start() - 50):match.end() + 50].replace("\n", " ")
                        found.append(f"{skill['name']} ({context.strip()})")
                    else:
                        found.append(skill["name"])
                    matched = True
                    break
            if not matched:
                missing.append(skill["name"])
        return found, missing

    def _match_simple_skills(self, skills, resume_text, resume_lower, verbose):
        """Match simple skill strings against resume, punctuation-safe."""
        found, missing = [], []
        for s in skills:
            pattern = rf"(?<!\w){re.escape(s.lower())}(?!\w)"
            match = re.search(pattern, resume_lower, flags=re.MULTILINE)
            if match:
                if verbose:
                    context = resume_text[max(0, match.start() - 50):match.end() + 50].replace("\n", " ")
                    found.append(f"{s} ({context.strip()})")
                else:
                    found.append(s)
            else:
                missing.append(s)
        return found, missing

    def display_combined_table(self, extracted, title, score=None):
        """Display found/missing skills in a combined category table."""
        table = Table(title=title, show_lines=True)
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Skills", style="white")

        for category, data in extracted.items():
            found_str = ", ".join(f"[green]{s}[/green]" for s in data["found"]) if data["found"] else "[dim]None[/dim]"
            missing_str = ", ".join(f"[dim]{s}[/dim]" for s in data["missing"]) if data["missing"] else ""
            combined_str = found_str
            if missing_str:
                combined_str += f"  |  {missing_str}"
            table.add_row(category, combined_str)

        console.print(table)
        if score is not None:
            console.print(f"[bold]ATS Compatibility Score:[/bold] {score}%")
