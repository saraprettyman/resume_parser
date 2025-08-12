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

# Blocklist terms that strongly indicate the candidate text is a degree/major, not a location.
_DEGREE_TERM_BLOCKLIST = {
    "science",
    "mathematics",
    "statistics",
    "computer",
    "data",
    "applied",
    "engineering",
    "arts",
    "business",
    "information",
    "systems",
    "intelligence",
    "analytics",
}

# Location regex: matches City, ST  OR City, Country (anchored to EOL).
# Also matches Remote/Hybrid/Onsite/Work From Home variants.
_LOCATION_RE = re.compile(
    r"\b("
    r"(?:[A-Za-z][A-Za-z .'\-]+,\s*(?:[A-Z]{2}|[A-Za-z][A-Za-z .'\-]+))"  # City, ST  or City, Country
    r"|(?:Remote|Hybrid|On[- ]?site|WFH|Work\s*From\s*Home)"               # Remote/Hybrid/Onsite
    r")\s*$",
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

    def _sanitize_location_candidate(self, cand: str) -> str | None:
        """
        Try to repair a location candidate that contains degree words.
        - If candidate looks like 'Statistics Logan, Utah', we convert -> 'Logan, Utah'.
        - If candidate still looks like degree text (e.g. 'Anticipatory Intelligence, Data Science'), return None.
        """
        if not cand:
            return None
        lc = cand.lower()
        # If candidate contains obvious degree words, try salvage
        if any(term in lc for term in _DEGREE_TERM_BLOCKLIST):
            parts = [p.strip() for p in cand.split(",")]
            if len(parts) >= 2:
                last_part = parts[-1]  # e.g. 'Utah'
                pre = " ".join(parts[:-1]).strip()  # e.g. 'Statistics Logan' or 'Computational and Applied Mathematics'
                if pre:
                    last_word = pre.split()[-1]  # e.g. 'Logan'
                    # simple validation of token
                    if re.match(r"^[A-Za-z][A-Za-z'\-]+$", last_word):
                        new_cand = f"{last_word}, {last_part}"
                        if not any(term in new_cand.lower() for term in _DEGREE_TERM_BLOCKLIST):
                            return new_cand
            return None
        return cand.strip()

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

            # Graduation Date (uses your DATE_RANGE pattern from config)
            grad_match = re.search(DATE_RANGE, text, re.IGNORECASE)
            grad_date = grad_match.group(0).strip() if grad_match else ""

            # 1) Location detection pass: scan first few lines for anchored location candidates
            location = ""
            for ln in lines[:3]:
                loc_match = _LOCATION_RE.search(ln)
                if loc_match:
                    raw_cand = loc_match.group(1).strip()
                    cand = self._sanitize_location_candidate(raw_cand)
                    if cand:
                        location = cand
                        break

            # 2) If still not found, try specifically on the degree line (sometimes location sits at end of degree line)
            if not location:
                degree_line_candidate = None
                for ln in lines:
                    if _DEGREE_KEYWORD_RE.search(ln):
                        degree_line_candidate = ln
                        break
                if degree_line_candidate:
                    loc_match = _LOCATION_RE.search(degree_line_candidate)
                    if loc_match:
                        raw_cand = loc_match.group(1).strip()
                        cand = self._sanitize_location_candidate(raw_cand)
                        if cand:
                            location = cand

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

            # If institution_line contains the location (same-line format), remove it
            if location and location in institution_line:
                institution_line = institution_line.replace(location, "").strip(" ,;:-")

            institution = institution_line

            # Degree & Emphasis
            degree_idx = None
            for i, ln in enumerate(lines):
                if _DEGREE_KEYWORD_RE.search(ln):
                    degree_idx = i
                    break
            degree_line = lines[degree_idx] if degree_idx is not None else (lines[1] if len(lines) > 1 else lines[0])

            # Remove location from degree_line if it's trailing there
            if location and location in degree_line:
                degree_line = degree_line.replace(location, "").strip(",;:- ")

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
