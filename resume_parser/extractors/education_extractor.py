"""Extractor for structured education history from resumes.

Parses the 'Education' section of a resume into structured fields like
institution, location, graduation date, degree, emphasis, GPA, minors,
and additional details.
"""
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

    def _normalize_text(self, section: str) -> tuple[str, list[str]]:
        text = section.replace("•", " ").replace("\t", " ").strip()
        text = re.sub(r"[ ]{2,}", " ", text)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return text, lines

    def _extract_grad_date(self, text: str) -> str:
        match = re.search(DATE_RANGE, text, re.IGNORECASE)
        return match.group(0).strip() if match else ""

    def _extract_location(self, lines: list[str]) -> str:
        for ln in lines[:3]:
            loc_match = re.search(LOCATION_PATTERN, ln, re.IGNORECASE)
            if loc_match:
                cand = self._sanitize_location_candidate(loc_match.group(1).strip())
                if cand:
                    return cand
        return ""

    def _extract_institution(self, lines: list[str], grad_date: str, location: str) -> str:
        gpa_re = re.compile(GPA_PATTERN, re.IGNORECASE)
        line = next((ln for ln in lines if not (
            gpa_re.search(ln) or
            re.search(MINORS_PATTERN, ln, re.IGNORECASE) or
            "project" in ln.lower()
        )), "")
        if grad_date:
            line = line.replace(grad_date, "")
        if location:
            line = line.replace(location, "")
        return line.strip(" ,;:-")

    def _extract_degree_emphasis(self, lines: list[str], location: str) -> tuple[str, str]:
        idx = next((i for i, ln in enumerate(lines)
                    if re.search(DEGREE_KEYWORD_PATTERN,
                                 ln, re.IGNORECASE)), None
        )
        degree_line = lines[idx] if idx is not None else (lines[1] if len(lines) > 1 else lines[0])
        if location:
            degree_line = degree_line.replace(location, "").strip(",;:- ")
        match = re.search(r"(?P<degree>(?:Bachelor(?:'s)?|Master(?:'s)?|Associate(?:'s)?|Doctor(?:ate)?|B\.S\.|M\.S\.|Ph\.?D)[^:,\n]*)", degree_line, re.IGNORECASE) # pylint: disable=line-too-long
        degree = match.group("degree").strip() if match else ""
        emphasis = degree_line.replace(degree, "").strip(" ,:-") if degree else ""
        return degree, emphasis

    def _extract_gpa(self, text: str) -> str:
        gpa_m = re.search(GPA_PATTERN, text, re.IGNORECASE)
        if gpa_m:
            if gpa_m.group(2):
                return f"{gpa_m.group(1)}/{gpa_m.group(2)}"
            return gpa_m.group(1)
        return ""

    def _extract_minors(self, text: str) -> str:
        minors_m = re.search(MINORS_PATTERN, text, re.IGNORECASE)
        return minors_m.group(1).strip().replace("\n", "; ") if minors_m else ""

    def _extract_details(
    self, text: str, lines: list[str],
    institution: str, degree: str,
    location: str, gpa: str, minors: str
    ) -> str:
        used_lines = {
            institution.strip(),
            degree.strip(),
            location.strip(),
            gpa.strip(),
            minors.strip()
        }
        details_parts = []

        # Extract from projects and scholarships
        for pattern in [PROJECTS_PATTERN, SCHOLARSHIPS_PATTERN]:
            m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if m:
                clean_text = re.sub(r"\s*\n\s*", "; ", m.group(1).strip())
                details_parts.append(clean_text)

        # Remaining unused lines
        for ln in lines:
            if ln.strip() in used_lines:
                continue
            if re.search(PROJECTS_PATTERN, ln, re.IGNORECASE):
                continue
            if re.search(SCHOLARSHIPS_PATTERN, ln, re.IGNORECASE):
                continue
            details_parts.append(ln.strip())

        return "; ".join(p for p in details_parts if p)



    def parse_education(self, section: str) -> list[dict]:
        """
        Parse the education section into structured items.
        """
        if not section.strip():
            return []

        text, lines = self._normalize_text(section)
        grad_date = self._extract_grad_date(text)
        location = self._extract_location(lines)
        institution = self._extract_institution(lines, grad_date, location)
        degree, emphasis = self._extract_degree_emphasis(lines, location)
        gpa_val = self._extract_gpa(text)
        minors_val = self._extract_minors(text)
        details_val = self._extract_details(text, lines, institution,
                                            degree, location, gpa_val,
                                            minors_val)

        return [{
            "Institution": institution,
            "Location": location,
            "Graduation Date": grad_date,
            "Degree & Emphasis": f"{degree}: {emphasis}" if emphasis
            and degree else emphasis or degree,
            "GPA": gpa_val,
            "Minors": minors_val,
            "Details": details_val
        }]
