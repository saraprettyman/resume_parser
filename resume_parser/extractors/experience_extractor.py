import re
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.section_finder import find_section
from config.patterns import (
    EXP_START,
    EXP_END,
    EXPERIENCE_ENTRY_PATTERN,
    DATE_RANGE_PATTERN,
    EXPERIENCE_LOCATION_PATTERN
)


class ExperienceExtractor(BaseExtractor):
    """
    Extractor for the 'Experience' section of a resume.

    This extractor:
        - Identifies the experience section based on start/end patterns.
        - Parses individual experience entries (job title, company, dates, location).
        - Extracts both free-text descriptions and bullet points for each job.

    Inherits:
        BaseExtractor: Provides normalization and shared extraction utilities.
    """

    def extract(self, file_path: str) -> dict:
        """
        Extract structured experience information from a resume.

        Args:
            file_path (str): Path to the resume file.

        Returns:
            dict: A dictionary containing:
                - "section" (str): Raw extracted experience section text.
                - "items" (list[dict]): List of extracted experience entries, each with:
                    - Job Title (str)
                    - Company (str)
                    - Location (str)
                    - Start Date (str)
                    - End Date (str)
                    - Details (str): Free text (non-bulleted) description.
                    - Bullets (list[str]): Bullet point descriptions.
        """
        text = self.normalize(read_resume(file_path))
        section_text = find_section(text, EXP_START, EXP_END)

        if not section_text:
            return {"section": "", "items": []}

        entry_pattern = re.compile(EXPERIENCE_ENTRY_PATTERN, re.MULTILINE | re.VERBOSE)
        date_re = re.compile(DATE_RANGE_PATTERN, flags=re.IGNORECASE)
        location_regex = re.compile(EXPERIENCE_LOCATION_PATTERN, re.IGNORECASE)

        items = []
        for match in entry_pattern.finditer(section_text):
            title = match.group("title").strip()
            company = match.group("company").strip()
            location = (match.group("location") or "").strip()
            start = match.group("start").strip()
            end = match.group("end").strip()
            details_text = (match.group("details") or "").strip()

            free_lines, bullets = self._extract_details(details_text, date_re, title, company, location_regex)
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
        """
        Separate bullet points from free text lines.

        Args:
            lines (list[str]): Lines of text from an experience entry.

        Returns:
            tuple[list[str], list[str]]:
                - Free text lines (non-bulleted content).
                - Bullet point lines (stripped of bullet characters).
        """
        bullets = []
        free_lines = []
        for ln in lines:
            s = ln.strip()
            if not s:
                continue
            # Match standard bullet markers
            if re.match(r'^[\u2022\-\*\•]\s*', s):
                content = re.sub(r'^[\u2022\-\*\•\s]{1,4}', '', s).strip()
                if content:
                    bullets.append(content)
            # Handle inline bullets separated by •
            elif "•" in s:
                parts = [p.strip() for p in s.split("•") if p.strip()]
                bullets.extend(parts)
            else:
                # Continuation of previous bullet or free text
                if bullets:
                    bullets[-1] += " " + s
                else:
                    free_lines.append(s)
        return free_lines, bullets

    def _extract_details(self, details_region, date_re, job_title, company, location_regex):
        """
        Clean and filter detail lines for an experience entry.

        Removes:
            - Lines matching job title or company name
            - Lines containing date patterns
            - Lines matching a location format

        Args:
            details_region (str): Raw details text from a job entry.
            date_re (Pattern): Compiled regex for detecting dates.
            job_title (str): Job title for the entry.
            company (str): Company name for the entry.
            location_regex (Pattern): Compiled regex for detecting locations.

        Returns:
            tuple[list[str], list[str]]:
                - Free text lines.
                - Bullet point lines.
        """
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
