# extractors/education_extractor.py
import re
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.section_finder import find_section
from config.patterns import EDU_START, EDU_END, DATE_RANGE, GPA_PATTERN

# helper small regexes we use locally
_DEGREE_KEYWORD_RE = re.compile(
    r"\b(?:Bachelor(?:'s)?|Master(?:'s)?|Associate(?:'s)?|Doctor(?:ate)?|B\.S\.|BSc|BS|M\.S\.|MS|Ph\.D\.|PhD)\b",
    re.IGNORECASE,
)

# common patterns used for extracting multi-line blocks
_PROJECTS_RE = re.compile(
    r"(?:Relevant Projects?|Projects?)\s*[:\-–]?\s*((?:.*?)(?=(?:\n\s*\n|$)))",
    re.IGNORECASE | re.DOTALL,
)
_MINORS_RE = re.compile(r"Minors?\s*[:\-–]?\s*([^\n|]+)", re.IGNORECASE)
_SCHOLARSHIPS_RE = re.compile(
    r"(?:Scholarships?|Awards?)\s*[:\-–]?\s*((?:.*?)(?=(?:\n\s*\n|$)))",
    re.IGNORECASE | re.DOTALL,
)
_GPA_RE = re.compile(
    r"(?:GPA|G\.P\.A)\s*[:\s]?\s*([0-4](?:[.,]\d{1,2})?)(?:\s*/\s*([0-4](?:[.,]\d{1,2})?))?",
    re.IGNORECASE,
)


class EducationExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        """
        Returns: { "section": <raw section text>, "items": [ {Institution, Location, Graduation Date,
                    "Degree & Emphasis", "GPA", "Minors", "Projects", "Scholarships / Awards" }, ... ] }
        """
        text = self.normalize(read_resume(file_path))
        section = find_section(text, EDU_START, EDU_END) or ""
        items = self.parse_education(section)
        return {"section": section, "items": items}

    def parse_education(self, section: str):
        items = []
        try:
            if not section or not section.strip():
                return items

            # normalize bullets/tabs and collapse spaces
            text = section.replace("•", " ").replace("\t", " ").strip()
            text = re.sub(r"[ ]{2,}", " ", text)
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if not lines:
                return items

            # Graduation Date
            grad_match = re.search(DATE_RANGE, text, re.IGNORECASE)
            grad_date = grad_match.group(0).strip() if grad_match else ""

            # Location detection early
            location = ""
            for ln in lines[:2]:
                loc_match = re.search(r"([A-Za-z][A-Za-z .'-]+,\s*[A-Za-z][A-Za-z .'-]+)$", ln)
                if loc_match:
                    location = loc_match.group(1).strip()
                    break

            # Institution: first line that’s not GPA, not projects, not minors
            institution_line = ""
            for ln in lines:
                if _GPA_RE.search(ln) or _MINORS_RE.search(ln) or "project" in ln.lower():
                    continue
                institution_line = ln
                break
            institution_line = institution_line.strip(" |,;-")
            if grad_date and grad_date in institution_line:
                institution_line = institution_line.replace(grad_date, "").strip(",;- ")

            institution = institution_line

            # Degree line
            degree_idx = None
            for i, ln in enumerate(lines):
                if _DEGREE_KEYWORD_RE.search(ln):
                    degree_idx = i
                    break
            degree_line = lines[degree_idx] if degree_idx is not None else (lines[1] if len(lines) > 1 else lines[0])
            if location and degree_line.endswith(location):
                degree_line = degree_line[: -len(location)].strip(",;:- ")

            degree_match = re.search(
                r"(?P<degree>(?:Bachelor(?:'s)?[^:,\n]*|Master(?:'s)?[^:,\n]*|Associate(?:'s)?[^:,\n]*|Doctor(?:ate)?[^:,\n]*|B\.S\.[^:,\n]*|M\.S\.[^:,\n]*|Ph\.?D[^:,\n]*))",
                degree_line,
                re.IGNORECASE,
            )
            degree = degree_match.group("degree").strip() if degree_match else ""
            emphasis = ""
            if ":" in degree_line:
                emphasis = degree_line.split(":", 1)[1].strip()
            elif degree:
                remainder = degree_line.replace(degree, "").strip(" ,:-")
                emphasis = remainder

            # GPA
            gpa_val = ""
            gpa_m = _GPA_RE.search(text)
            if gpa_m:
                gpa_val = f"{gpa_m.group(1)}/{gpa_m.group(2)}" if gpa_m.group(2) else gpa_m.group(1)

            # Minors (flattened)
            minors_val = ""
            minors_m = _MINORS_RE.search(text)
            if minors_m:
                minors_val = minors_m.group(1).strip().replace("\n", "; ")

            # Projects (flattened)
            projects_val = ""
            projects_m = _PROJECTS_RE.search(text)
            if projects_m:
                projects_val = re.sub(r"\s*\n\s*", "; ", projects_m.group(1).strip())

            # Scholarships / Awards (flattened)
            scholarships_val = ""
            scholarships_m = _SCHOLARSHIPS_RE.search(text)
            if scholarships_m:
                scholarships_val = re.sub(r"\s*\n\s*", "; ", scholarships_m.group(1).strip())

            # Final degree/emphasis string
            degree_emphasis = degree
            if emphasis:
                degree_emphasis = f"{degree_emphasis}: {emphasis}" if degree_emphasis else emphasis

            items.append({
                "Institution": institution,
                "Location": location,
                "Graduation Date": grad_date,
                "Degree & Emphasis": degree_emphasis,
                "GPA": gpa_val,
                "Minors": minors_val,
                "Projects": projects_val,
                "Scholarships / Awards": scholarships_val,
            })

            return items

        except Exception:
            return [{
                "Institution": section.strip(),
                "Location": "",
                "Graduation Date": "",
                "Degree & Emphasis": "",
                "GPA": "",
                "Minors": "",
                "Projects": "",
                "Scholarships / Awards": "",
            }]
