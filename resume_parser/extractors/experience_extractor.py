"""Experience section extractor for resumes.

This module contains the ExperienceExtractor class, which parses
the 'Experience' section of resumes in various formats, including:
- Pipe-delimited headers (Title | Company | Location | Dates)
- Stacked-line headers (Title \n Company \n Location \n Dates)
- Mixed formats
"""

import re
from resume_parser.extractors.base_extractor import BaseExtractor
from resume_parser.utils.file_reader import read_resume
from resume_parser.utils.section_finder import find_section
from resume_parser.config.patterns import (
    EXP_START,
    EXP_END,
    EXPERIENCE_ENTRY_PATTERN,
    DATE_RANGE_PATTERN,
    EXPERIENCE_LOCATION_PATTERN,
    EXPERIENCE_PIPE_PATTERN_4,
    EXPERIENCE_PIPE_PATTERN_3,
    EXPERIENCE_PIPE_PATTERN_COMPANY_TITLE
)


class ExperienceExtractor(BaseExtractor):
    """
    Hybrid extractor for the 'Experience' section of a resume.
    Handles:
      - Pipe-delimited headers (Title | Company | Location | Dates)
      - Stacked-line headers (Title \n Company \n Location \n Dates)
      - Mixed formats
    """

    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        section_text = find_section(text, EXP_START, EXP_END)

        if not section_text:
            return {"section": "", "items": []}

        date_re = re.compile(DATE_RANGE_PATTERN, flags=re.IGNORECASE)
        location_regex = re.compile(EXPERIENCE_LOCATION_PATTERN, re.IGNORECASE)

        # --- Compile all patterns ---
        pipe_pattern_company_title = re.compile(
            EXPERIENCE_PIPE_PATTERN_COMPANY_TITLE,  # NEW
            re.MULTILINE | re.VERBOSE | re.IGNORECASE
        )
        pipe_pattern_4 = re.compile(
            EXPERIENCE_PIPE_PATTERN_4,
            re.MULTILINE | re.VERBOSE | re.IGNORECASE
        )
        pipe_pattern_3 = re.compile(
            EXPERIENCE_PIPE_PATTERN_3,
            re.MULTILINE | re.VERBOSE | re.IGNORECASE
        )
        entry_pattern = re.compile(
            EXPERIENCE_ENTRY_PATTERN,
            re.MULTILINE | re.VERBOSE
        )

        # --- Try patterns in priority order ---
        matches = []
        for label, pattern in [
            ("COMPANY | TITLE + DATES", pipe_pattern_company_title),
            ("PIPE 4", pipe_pattern_4),
            ("PIPE 3", pipe_pattern_3),
            ("ENTRY", entry_pattern),
        ]:
            matches = list(pattern.finditer(section_text))
            if matches:
                break  # stop on first matching format

        # --- Debug if no matches found ---
        if not matches:
            print("DEBUG: No matches found — checking why...")
            print("=== Section Text ===")
            print(section_text)
            print("====================")
            for label, pattern in [
                ("COMPANY | TITLE + DATES", pipe_pattern_company_title),
                ("PIPE 4", pipe_pattern_4),
                ("PIPE 3", pipe_pattern_3),
                ("ENTRY", entry_pattern),
            ]:
                print(f"\n--- Testing pattern: {label} ---")
                test_matches = list(pattern.finditer(section_text))
                print(f"Found {len(test_matches)} matches")
                for i, m in enumerate(test_matches, 1):
                    print(f"Match {i}: {m.groupdict()}")

        # --- Build items ---
        items = []
        for match in matches:
            gd = match.groupdict()
            title = (gd.get("title") or "").strip()
            company = (gd.get("company") or "").strip()
            location = (gd.get("location") or "").strip()
            start = (gd.get("start") or "").strip()
            end = (gd.get("end") or "").strip()
            details_text = (gd.get("details") or "").strip()

            free_lines, bullets = self._extract_details(
                details_text,
                date_re,
                title,
                company,
                location_regex
            )
            free_text = "\n".join(free_lines).strip()

            items.append({
                "Job Title": title,
                "Company": company,
                "Location": location,
                "Start Date": start,
                "End Date": end,
                "Details": free_text,
                "Bullets": bullets
            })

        return {"section": section_text, "items": items}

    def _collect_bullets(self, lines):
        bullets = []
        free_lines = []
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            if re.match(r'^[\u2022\-\*\•]\s*', s):
                content = re.sub(r'^[\u2022\-\*\•\s]{1,4}', '', s).strip()
                if content:
                    bullets.append(content)
            elif "•" in s:
                parts = [p.strip() for p in s.split("•") if p.strip()]
                bullets.extend(parts)
            else:
                if bullets:
                    bullets[-1] += " " + s
                else:
                    free_lines.append(s)
        return free_lines, bullets

    def _extract_details(self, details_region, date_re, job_title, company, location_regex):
        if not details_region:
            return [], []

        raw_lines = [ln for ln in re.split(r"\n+", details_region)]
        filtered = []
        for ln in raw_lines:
            ln_str = ln.strip()
            if not ln_str:
                continue
            if ln_str == job_title or ln_str == company:
                continue
            if date_re.search(ln_str):
                continue
            if location_regex.fullmatch(ln_str):
                continue
            filtered.append(ln)

        return self._collect_bullets(filtered)
    