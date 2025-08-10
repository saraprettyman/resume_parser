import re
from rich.table import Table
from rich.console import Console
from .file_reader import read_resume

console = Console()

class ATSEducationExperienceExtractor:
    def __init__(self):
        pass

    def extract_edu_exp(self, file_path):
        text = read_resume(file_path)

        results = {}

        # --- EDUCATION ---
        extracted_edu = self._extract_education(text)
        results["Education"] = {
            "status": "Found" if extracted_edu else "Missing",
            "value": extracted_edu or ""
        }

        # --- WORK EXPERIENCE ---
        extracted_work = self._extract_work_experience(text)
        results["Work Experience"] = {
            "status": "Found" if extracted_work else "Missing",
            "value": extracted_work or ""
        }

        return results

    # ----------------------
    # EXTRACTION METHODS
    # ----------------------

    def _extract_education(self, text):
        edu_keywords = [
            r"bachelor",
            r"master",
            r"ph\.?d",
            r"associate",
            r"degree",
            r"diploma",
            r"university",
            r"college"
        ]
        for keyword in edu_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                return keyword
        return None

    def _extract_work_experience(self, text):
        work_keywords = [
            r"experience",
            r"employment",
            r"professional history",
            r"work history"
        ]
        for keyword in work_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                return keyword
        return None

    # ----------------------
    # DISPLAY METHOD
    # ----------------------

    def display_edu_exp_table(self, edu_exp_results):
        table = Table(title="", show_lines=True, expand=True)
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Status", style="white")
        table.add_column("Extracted Value", style="white")

        for category, data in edu_exp_results.items():
            status_style = "[green]Found[/green]" if data["status"] == "Found" else "[red]Missing[/red]"
            table.add_row(category, status_style, data["value"])

        console.print(table)
