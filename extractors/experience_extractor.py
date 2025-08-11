# extractors/experience_extractor.py
import re
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.section_finder import find_section
from config.patterns import EXP_START, EXP_END, DATE_RANGE


class ExperienceExtractor(BaseExtractor):
    """
    Extracts structured experience information from a resume file.
    Uses date patterns as anchors, falls back to paragraph-based parsing if dates are not detected.
    """

    def extract(self, file_path: str) -> dict:
        # Read & normalize resume text
        raw_text = read_resume(file_path) or ""
        normalized_text = self.normalize(raw_text)

        # Locate the 'Experience' section
        section = find_section(normalized_text, EXP_START, EXP_END)
        section = str(section or "").strip()

        # Parse experiences from section
        items = self.parse_experience(section)

        # Return structured output
        return {
            "section": section,
            "items": items
        }

    def parse_experience(self, content: str):
        """Parses experience section into structured entries."""
        if not content:
            return []

        # Normalize whitespace & dashes
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        content = re.sub(r"[–—]", "-", content)
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Date regex compiled with DOTALL for multi-line matches
        date_re = re.compile(DATE_RANGE, flags=re.IGNORECASE | re.DOTALL)
        matches = list(date_re.finditer(content))

        # If no date matches found → fallback
        if not matches:
            return self._parse_by_paragraphs(content)

        # Merge fragmented date matches
        merged_dates = []
        cur_start, cur_end = matches[0].start(), matches[0].end()
        for m in matches[1:]:
            if re.fullmatch(r"[\s\-\–\—,\.]*", content[cur_end:m.start()]):
                cur_end = m.end()
            else:
                merged_dates.append((cur_start, cur_end))
                cur_start, cur_end = m.start(), m.end()
        merged_dates.append((cur_start, cur_end))

        # Patterns for identifying company names & job titles
        company_kw_regex = re.compile(
            r"\b(Inc|LLC|Corp|Company|Co\.|Ltd|LLP|GmbH|Software|Solutions|Systems|Labs|Group|Technologies|University|Institute|School|Remote|Health|Fitness)\b",
            re.IGNORECASE
        )
        location_regex = re.compile(r"[A-Za-z .]+,\s*[A-Za-z]{2,}", re.IGNORECASE)
        title_kw_regex = re.compile(
            r"\b(Engineer|Developer|Manager|Director|Lead|Specialist|Analyst|Consultant|Tester|QA|SQA|Quality|Product|Architect|Coordinator|Administrator)\b",
            re.IGNORECASE
        )

        items = []
        for i, (mstart, mend) in enumerate(merged_dates):
            # Extract date string
            date_str = re.sub(r"[–—]", "-", content[mstart:mend].strip())
            start_date, end_date = self._split_date(date_str)

            # Header (before date) and details (after date)
            prev_anchor = content.rfind("\n\n", 0, mstart)
            header_text = content[prev_anchor + 2 if prev_anchor != -1 else 0:mstart].strip()
            next_start = merged_dates[i + 1][0] if i + 1 < len(merged_dates) else len(content)
            details_text = content[mend:next_start].strip()

            # Candidate lines for company/title detection
            pre_lines = [ln.strip() for ln in re.split(r"\n+", header_text) if ln.strip()]
            post_lines = [ln.strip() for ln in re.split(r"\n+", details_text) if ln.strip()]
            candidates = (pre_lines[-2:] if pre_lines else []) + (post_lines[:2] if post_lines else [])

            # Identify company
            company = next((ln for ln in candidates if company_kw_regex.search(ln) or location_regex.search(ln)), "")
            if not company and post_lines and post_lines[0] != company:
                company = post_lines[0]

            # Identify job title
            job_title = ""
            if pre_lines:
                candidate = pre_lines[-1]
                if candidate != company:
                    job_title = candidate
                elif len(pre_lines) > 1:
                    job_title = pre_lines[-2]
            if not job_title:
                job_title = next((ln for ln in candidates if title_kw_regex.search(ln)), "")

            # Clean details & extract bullets
            detail_lines, bullets = self._extract_details(details_text, date_re, job_title, company, location_regex)
            free_text = "\n".join(detail_lines).strip()

            items.append({
                "Job Title": job_title,
                "Company": company,
                "Start Date": start_date,
                "End Date": end_date,
                "Details": free_text,
                "Bullets": bullets
            })

        return items

    def _split_date(self, date_str: str):
        """Splits a date string into start and end."""
        if "-" in date_str:
            parts = [p.strip() for p in date_str.split("-", 1)]
            return parts[0], parts[1]
        return date_str, ""

    def _extract_details(self, details_region, date_re, job_title, company, location_regex):
        """Cleans detail lines and separates bullets."""
        detail_lines = []
        for ln in re.split(r"\n+", details_region):
            ln = ln.strip()
            if not ln or date_re.search(ln) or ln in (job_title, company):
                continue
            if location_regex.fullmatch(ln):
                continue
            detail_lines.append(ln)

        bullets, free_lines = [], []
        for ln in detail_lines:
            m = re.match(r"^[\u2022\-\*\•\s]{0,4}(.*)$", ln)
            if m and (ln.startswith(("•", "-", "*")) or ln.strip().startswith("•")):
                if (b := m.group(1).strip()):
                    bullets.append(b)
            elif "•" in ln:
                bullets.extend([p.strip() for p in ln.split("•") if p.strip()])
            else:
                free_lines.append(ln)

        return free_lines, bullets

    def _parse_by_paragraphs(self, content: str):
        """Fallback: parse section by paragraph blocks when dates are missing."""
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", re.sub(r"\n{2,}", "\n\n", content)) if p.strip()]
        items = []

        for block in paragraphs:
            block = re.sub(r"\n+", " ", block)  # join wrapped lines
            date_match = re.search(DATE_RANGE, block, flags=re.IGNORECASE)
            start_date, end_date = self._split_date(re.sub(r"[–—]", "-", date_match.group(0).strip())) if date_match else ("", "")

            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue

            # Try "Title @ Company" split
            job_title, company, detail_lines = lines[0], "", []
            split = re.split(r"\s+(?:@| at | - |—|–|\|)\s+", lines[0], maxsplit=1, flags=re.IGNORECASE)
            if len(split) >= 2:
                job_title, company = split[0], split[1]
                detail_lines = lines[1:]
            elif len(lines) > 1:
                company = lines[1]
                detail_lines = lines[2:]

            bullets, free_lines = [], []
            for ln in detail_lines:
                if re.search(DATE_RANGE, ln):
                    continue
                m = re.match(r"^[\u2022\-\*\•\s]{0,4}(.*)$", ln)
                if m and m.group(1).strip():
                    bullets.append(m.group(1).strip())
                else:
                    free_lines.append(ln)

            items.append({
                "Job Title": job_title,
                "Company": company,
                "Start Date": start_date,
                "End Date": end_date,
                "Details": "\n".join(free_lines).strip(),
                "Bullets": bullets
            })

        return items
