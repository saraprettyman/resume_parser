import re
import phonenumbers
from rich.table import Table
from rich.console import Console
from .file_reader import read_resume

console = Console()

class ProfileExtractor:
    def __init__(self):
        pass

    def extract_profile_info(self, file_path):
        text = read_resume(file_path)

        results = {}

        # --- NAME ---
        extracted_name = self._extract_name(text)
        results["Name"] = {
            "status": "Found" if extracted_name else "Missing",
            "value": extracted_name or ""
        }

        # --- PHONE ---
        extracted_phone = self._extract_phone(text)
        results["Phone Number"] = {
            "status": "Found" if extracted_phone else "Missing",
            "value": extracted_phone or ""
        }

        # --- EMAIL ---
        extracted_email = self._extract_email(text)
        results["Email"] = {
            "status": "Found" if extracted_email else "Missing",
            "value": extracted_email or ""
        }

        # --- LINKEDIN ---
        extracted_linkedin = self._extract_linkedin(text)
        results["LinkedIn"] = {
            "status": "Found" if extracted_linkedin else "Missing",
            "value": extracted_linkedin or ""
        }

        # --- GITHUB ---
        extracted_github = self._extract_github(text)
        results["GitHub"] = {
            "status": "Found" if extracted_github else "Missing",
            "value": extracted_github or ""
        }

        # --- CITIZENSHIP / WORK AUTHORIZATION ---
        explicit_citizenship = self._extract_citizenship(text)
        if explicit_citizenship:
            results["Citizenship / Work Authorization"] = {
                "status": "Found",
                "value": explicit_citizenship
            }
        else:
            inferred_citizenship = self._infer_citizenship(text, extracted_phone)
            results["Citizenship / Work Authorization"] = {
                "status": "Found" if inferred_citizenship else "Missing",
                "value": inferred_citizenship or ""
            }

        return results

    # ----------------------
    # EXTRACTION METHODS
    # ----------------------

    def _extract_name(self, text):
        lines = text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            if 2 <= len(first_line.split()) <= 4:
                return first_line
        return None

    def _extract_phone(self, text):
        for match in phonenumbers.PhoneNumberMatcher(text, "US"):
            if phonenumbers.is_possible_number(match.number):
                return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.NATIONAL)
        return None

    def _extract_email(self, text):
        match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        return match.group(0) if match else None

    def _extract_linkedin(self, text):
        match = re.search(r"(https?:\/\/)?(www\.)?linkedin\.com\/[A-Za-z0-9\/\-_]+", text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_github(self, text):
        match = re.search(r"(https?:\/\/)?(www\.)?github\.com\/[A-Za-z0-9\/\-_]+", text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_citizenship(self, text):
        patterns = [
            r"U\.?S\.?\s+(Citizen|Citizenship)",
            r"Authorized to work in the U\.?S\.?",
            r"Permanent Resident",
            r"Green Card Holder",
        ]
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return "Explicitly stated: " + re.search(pat, text, re.IGNORECASE).group(0)
        return None

    def _infer_citizenship(self, text, phone):
        evidence = []
        score = 0

        # U.S. phone number
        if phone and re.search(r"\(\d{3}\)\s\d{3}-\d{4}", phone):
            evidence.append("phone_us")
            score += 40

        # U.S. location keywords
        if re.search(r"\b(USA|United States|[A-Z]{2})\b", text):
            evidence.append("location_us")
            score += 60

        if score >= 50:
            return f"Likely US citizen / authorized — {score}% — evidence: {', '.join(evidence)}"
        return None

    # ----------------------
    # DISPLAY METHOD
    # ----------------------

    def display_profile_table(self, profile_results):
        table = Table(title="", show_lines=True, expand=True)
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Status", style="white")
        table.add_column("Extracted Value", style="white")

        for category, data in profile_results.items():
            status_style = "[green]Found[/green]" if data["status"] == "Found" else "[red]Missing[/red]"
            table.add_row(category, status_style, data["value"])

        console.print(table)
