# extractors/education_extractor.py
import re
from typing import Optional
from resume_parser.extractors.base_extractor import BaseExtractor
from resume_parser.utils.file_reader import read_resume
from resume_parser.utils.section_finder import find_section
from resume_parser.config.patterns import (
    EDU_START, EDU_END, DATE_RANGE, GPA_PATTERN,
    DEGREE_KEYWORD_PATTERN, PROJECTS_PATTERN, MINORS_PATTERN,
    SCHOLARSHIPS_PATTERN, LOCATION_PATTERN, DEGREE_TERM_BLOCKLIST
) 

class EducationExtractor(BaseExtractor):
    """
    Extracts structured education history from a resume file.

    **Output Structure**:
    {
        "section": <raw education section text>,
        "items": [
            {
                "Institution": str,
                "Location": str,
                "Graduation Date": str,
                "Degree & Emphasis": str,
                "GPA": str,
                "Minors": str,
                "Details": str
            },
            ...
        ]
    }
    """

    def extract(self, file_path: str) -> dict:
        """
        Reads the resume file, finds the Education section, and parses it into structured fields.
        """
        text = self.normalize(read_resume(file_path))
        section = find_section(text, EDU_START, EDU_END) or ""
        items = self.parse_education(section)
        return {"section": section, "items": items}

    def _sanitize_location_candidate(self, cand: str) -> Optional[str]:
        """
        Clean up and validate a potential location string.
        
        - If the string contains degree keywords, we attempt to strip them out.
        - If it still looks like degree text after cleanup, return None.
        - Otherwise, return a normalized "City, State" style string.
        
        Example:
            "Statistics Logan, Utah" → "Logan, Utah"
            "Anticipatory Intelligence, Data Science" → None
        """
        if not cand:
            return None
        lc = cand.lower()
        if any(term in lc for term in DEGREE_TERM_BLOCKLIST):
            parts = [p.strip() for p in cand.split(",")]
            if len(parts) >= 2:
                last_part = parts[-1]
                pre = " ".join(parts[:-1]).strip()
                if pre:
                    last_word = pre.split()[-1]
                    if re.match(r"^[A-Za-z][A-Za-z'\-]+$", last_word):
                        new_cand = f"{last_word}, {last_part}"
                        if not any(term in new_cand.lower() for term in DEGREE_TERM_BLOCKLIST):
                            return new_cand
            return None
        return cand.strip()

    def parse_education(self, section: str) -> list[dict]:
        """
        Parse the education section text into structured items.
        
        Handles:
        - Institution name
        - Location
        - Graduation date
        - Degree + Emphasis
        - GPA
        - Minors
        - Project and scholarship details
        - Any remaining descriptive details
        """
        items = []
        try:
            if not section.strip():
                return items

            # Normalize text and split into lines
            text = section.replace("•", " ").replace("\t", " ").strip()
            text = re.sub(r"[ ]{2,}", " ", text)
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if not lines:
                return items

            # Graduation Date
            grad_match = re.search(DATE_RANGE, text, re.IGNORECASE)
            grad_date = grad_match.group(0).strip() if grad_match else ""

            # Location
            location = ""
            for ln in lines[:3]:  # Check early lines first
                loc_match = re.search(LOCATION_PATTERN, ln, re.IGNORECASE)
                if loc_match:
                    cand = self._sanitize_location_candidate(loc_match.group(1).strip())
                    if cand:
                        location = cand
                        break
            if not location:  # Secondary check inside degree lines
                degree_line_candidate = next((ln for ln in lines if re.search(DEGREE_KEYWORD_PATTERN, ln, re.IGNORECASE)), None)
                if degree_line_candidate:
                    loc_match = re.search(LOCATION_PATTERN, degree_line_candidate, re.IGNORECASE)
                    if loc_match:
                        cand = self._sanitize_location_candidate(loc_match.group(1).strip())
                        if cand:
                            location = cand

            # Institution
            GPA_RE = re.compile(GPA_PATTERN, re.IGNORECASE)
            institution_line = next(
                (ln for ln in lines if not (GPA_RE.search(ln) or re.search(MINORS_PATTERN, ln, re.IGNORECASE) or "project" in ln.lower())),
                ""
            ).strip(" |,;-")
            if grad_date:
                institution_line = institution_line.replace(grad_date, "").strip(",;- ")
            if location:
                institution_line = institution_line.replace(location, "").strip(" ,;:-")
            institution = institution_line

            # Degree & Emphasis
            degree_idx = next((i for i, ln in enumerate(lines) if re.search(DEGREE_KEYWORD_PATTERN, ln, re.IGNORECASE)), None)
            degree_line = lines[degree_idx] if degree_idx is not None else (lines[1] if len(lines) > 1 else lines[0])
            if location:
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
                emphasis = degree_line.replace(degree, "").strip(" ,:-")

            # GPA
            gpa_val = ""
            gpa_m = GPA_RE.search(text)
            if gpa_m:
                gpa_val = f"{gpa_m.group(1)}/{gpa_m.group(2)}" if gpa_m.group(2) else gpa_m.group(1)

            # Minors
            minors_val = ""
            minors_m = re.search(MINORS_PATTERN, text, re.IGNORECASE)
            if minors_m:
                minors_val = minors_m.group(1).strip().replace("\n", "; ")

            # Details
            details_parts = []

            projects_m = re.search(PROJECTS_PATTERN, text, re.IGNORECASE | re.DOTALL)
            if projects_m:
                details_parts.append(re.sub(r"\s*\n\s*", "; ", projects_m.group(1).strip()))

            scholarships_m = re.search(SCHOLARSHIPS_PATTERN, text, re.IGNORECASE | re.DOTALL)
            if scholarships_m:
                details_parts.append(re.sub(r"\s*\n\s*", "; ", scholarships_m.group(1).strip()))

            # Remaining lines that aren't already used
            used_lines = {
                institution.strip(),
                degree_line.strip(),
                location.strip(),
                gpa_val.strip(),
                minors_val.strip(),
            }
            for ln in lines:
                if not ln or ln.strip() in used_lines:
                    continue
                if re.search(PROJECTS_PATTERN, ln, re.IGNORECASE) or re.search(SCHOLARSHIPS_PATTERN, ln, re.IGNORECASE):
                    continue
                details_parts.append(ln.strip())

            details_val = "; ".join(p for p in details_parts if p)


            # Final degree + emphasis
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
                "Details": details_val
            })
            return items

        except Exception:
            # Fallback: return raw section text as institution only
            return [{
                "Institution": section.strip(),
                "Location": "",
                "Graduation Date": "",
                "Degree & Emphasis": "",
                "GPA": "",
                "Minors": "",
                "Details": ""
            }]
