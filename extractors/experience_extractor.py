# extractors/experience_extractor.py
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.section_finder import find_section
from config.patterns import EXP_START, EXP_END, DATE_RANGE
import re

class ExperienceExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        section = find_section(text, EXP_START, EXP_END)
        items = self._parse_experience(section)
        return {"section": section, "items": items}

    def _parse_experience(self, content: str):
        if not content:
            return []
        # split by double newline blocks
        blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]
        items = []
        for block in blocks:
            date_match = re.search(DATE_RANGE, block)
            date_str = date_match.group(0).strip() if date_match else ""
            start_date = end_date = ""
            if date_str:
                clean = re.sub(r"[–—]", "-", date_str)
                if "-" in clean:
                    p = [part.strip() for part in clean.split("-", 1)]
                    start_date = p[0]
                    end_date = p[1]
                else:
                    start_date = clean

            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            # first line often contains title + company
            title_line = lines[0] if lines else ""
            if date_str and date_str in title_line:
                title_line = title_line.replace(date_str, "").strip()

            # try split by " at " or " @ " or " - "
            split = re.split(r"\s+(?:@| at | - |—|–|\|)\s+", title_line, maxsplit=1, flags=re.IGNORECASE)
            if len(split) >= 2:
                job_title = split[0].strip()
                company = split[1].strip()
                detail_lines = lines[1:]
            else:
                # maybe company on second line
                if len(lines) > 1 and re.search(r"(Inc|LLC|Corp|Company|Co\.|Ltd|University|Institute|School)", lines[1], re.IGNORECASE):
                    job_title = title_line
                    company = lines[1]
                    detail_lines = lines[2:]
                else:
                    job_title = title_line
                    company = ""
                    detail_lines = lines[1:]

            # filter out date-only or location-only lines
            filtered = []
            for ln in detail_lines:
                if re.search(DATE_RANGE, ln):
                    continue
                if re.fullmatch(r"[A-Za-z .]+,\s*[A-Za-z]{2,}", ln):
                    continue
                filtered.append(ln)

            bullets = []
            free_lines = []
            for ln in filtered:
                m = re.match(r"^[\u2022\-\*\•\s]{1,4}(.*)$", ln)
                if m:
                    b = m.group(1).strip()
                    if b:
                        bullets.append(b)
                else:
                    free_lines.append(ln)

            details_text = "\n".join(free_lines).strip()

            items.append({
                "Job Title": job_title,
                "Company": company,
                "Start Date": start_date,
                "End Date": end_date,
                "Details": details_text,
                "Bullets": bullets
            })
        return items
