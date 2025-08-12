# extractors/experience_extractor.py
import re
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.section_finder import find_section
from config.patterns import EXP_START, EXP_END  # keep in case other parts need them


class ExperienceExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        section_text = find_section(
            text,
            ["experience", "work history", "employment"],
            ["projects", "education", "skills"]
        )

        if not section_text:
            return {"section": "", "items": []}

        entry_pattern = re.compile(
            r"^"  # anchor at start of line for repeated matches
            r"(?P<title>[^\n]+?)\s+"  # Job title (greedy-ish, stops at date)
            r"(?P<start>[A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*"
            r"(?P<end>(?:[A-Za-z]{3,9}\s+\d{4}|Present))\s*\n"
            r"(?P<company>[^\n]+)"  # Company line
            r"(?:\s+(?P<location>[^\n]+))?"  # Optional location
            # details: stop when a new header is detected (either "Title Month YYYY - Month YYYY" or "Month YYYY - Month YYYY")
            r"(?:\n(?P<details>(?:(?!^(?:[^\n]+?\s+(?:[A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*(?:[A-Za-z]{3,9}\s+\d{4}|Present)|(?:[A-Za-z]{3,9}\s+\d{4})\s*[-–]\s*(?:[A-Za-z]{3,9}\s+\d{4}|Present))).*(?:\n|$))*))?",
            re.MULTILINE
        )

        # date and location regexes for detail filtering (kept similar to your other flow)
        month_names = (
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        )
        date_token = rf"(?:{month_names}\s+\d{{4}}|\d{{4}})"
        date_range_pattern = rf"({date_token})\s*(?:-|–|to|—)\s*(Present|present|{date_token})"
        date_re = re.compile(date_range_pattern, flags=re.IGNORECASE)

        location_regex = re.compile(
            r"^(?:[A-Za-z][A-Za-z .'\-]+,\s*(?:[A-Z]{2}|\d{4,5}|[A-Za-z][A-Za-z .'\-]+))$"
            r"|^(?:Remote|Hybrid|On[- ]?site|WFH|Work\s*From\s*Home)$",
            re.IGNORECASE,
        )

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
        Given a list of lines (already filtered), returns (free_lines, bullets).
        - Lines starting with • - * are new bullets.
        - Lines containing inline '•' are split into multiple bullets.
        - Other lines are treated as continuations of the previous bullet if one exists,
        otherwise they are treated as free/detail text.
        """
        bullets = []
        free_lines = []

        for ln in lines:
            s = ln.strip()
            if not s:
                continue

            # starts with an explicit bullet marker
            if re.match(r'^[\u2022\-\*\•]\s*', s):
                content = re.sub(r'^[\u2022\-\*\•\s]{1,4}', '', s).strip()
                if content:
                    bullets.append(content)
            # contains inline bullets (e.g. "foo • bar • baz")
            elif "•" in s:
                parts = [p.strip() for p in s.split("•") if p.strip()]
                bullets.extend(parts)
            else:
                # continuation: attach to last bullet, or if none, treat as free/detail text
                if bullets:
                    bullets[-1] = bullets[-1] + " " + s
                else:
                    free_lines.append(s)

        return free_lines, bullets


    def _extract_details(self, details_region, date_re, job_title, company, location_regex):
        """
        Filter out lines that are job headers, dates, or locations; then collect bullets,
        merging wrapped lines into previous bullets when appropriate.
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

        free_lines, bullets = self._collect_bullets(filtered)
        return free_lines, bullets


    def _parse_by_paragraphs(self, content: str):
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", re.sub(r"\n{2,}", "\n\n", content)) if p.strip()]
        items = []
        for block in paragraphs:
            block_joined = re.sub(r"\n+", " ", block).strip()
            date_match = re.search(r"(?:Jan(?:uary)?|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}|\b\d{4}\b", block_joined, flags=re.IGNORECASE)
            start_date = end_date = ""
            if date_match:
                dt = re.sub(r"[–—]", "-", date_match.group(0))
                if "-" in dt:
                    parts = [p.strip() for p in dt.split("-", 1)]
                    start_date, end_date = parts[0], parts[1]
                else:
                    start_date = dt.strip()

            # split title/company heuristically
            first_line = block.splitlines()[0].strip() if "\n" in block else block_joined
            split = re.split(r"\s+(?:@| at | - |—|–|\|)\s+", first_line, maxsplit=1, flags=re.IGNORECASE)
            job_title, company = (split[0].strip(), split[1].strip()) if len(split) == 2 else (first_line.strip(), "")

            lines = [ln.strip() for ln in re.split(r"\n+", block) if ln.strip()]
            content_lines = lines[1:] if len(lines) > 1 else []
            free_lines, bullets = self._collect_bullets(content_lines)

            items.append({
                "Job Title": job_title,
                "Company": company,
                "Start Date": start_date,
                "End Date": end_date,
                "Details": " ".join(free_lines).strip(),
                "Bullets": bullets
            })
        return items
