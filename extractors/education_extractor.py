# extractors/education_extractor.py
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.section_finder import find_section
from config.patterns import EDU_START, EDU_END, MONTH_YEAR, DATE_RANGE, DEGREE_PATTERNS, GPA_PATTERN
import re

class EducationExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        section = find_section(text, EDU_START, EDU_END)
        items = self._parse_education(section)
        return {"section": section, "items": items}

    def _parse_education(self, content: str):
        if not content:
            return []
        blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]
        items = []
        degree_re = re.compile("|".join(DEGREE_PATTERNS), re.IGNORECASE)
        gpa_re = re.compile(GPA_PATTERN, re.IGNORECASE)

        for block in blocks:
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            institution = ""
            grad_date = ""
            degree = ""
            gpa = ""
            # detect grad date first
            m = re.search(MONTH_YEAR, block, re.IGNORECASE)
            if m:
                grad_date = m.group(0)
            else:
                y = re.search(r"\b(19|20)\d{2}\b", block)
                if y:
                    grad_date = y.group(0)

            # degree
            d = degree_re.search(block)
            if d:
                degree = d.group(0).strip()

            # gpa
            g = gpa_re.search(block)
            if g:
                gpa_main = g.group(1).replace(",", ".")
                if g.group(2):
                    g = f"{gpa_main}/{g.group(2).replace(',', '.')}"
                else:
                    g = gpa_main
                gpa = g

            # institution detection
            details_lines = []
            for ln in lines:
                if re.search(r"(University|College|Institute|School|Academy|School of)", ln, re.IGNORECASE):
                    institution = ln
                    idx = lines.index(ln)
                    details_lines = lines[idx+1:]
                    break
            if not institution and lines:
                institution = lines[0]
                details_lines = lines[1:]
            # clean details
            cleaned = []
            for ln in details_lines:
                if re.search(DATE_RANGE, ln):
                    continue
                if gpa_re.search(ln):
                    continue
                cleaned.append(ln)
            # bullets + free text
            bullets = []
            free_lines = []
            for ln in cleaned:
                m2 = re.match(r"^[\u2022\-\*\•\s]{1,4}(.*)$", ln)
                if m2:
                    v = m2.group(1).strip()
                    if v:
                        bullets.append(v)
                else:
                    free_lines.append(ln)
            details_text = "\n".join(free_lines).strip()

            items.append({
                "Institution": institution,
                "Graduation Date": grad_date,
                "Degree": degree,
                "GPA": gpa,
                "Details": details_text,
                "Bullets": bullets
            })
        return items
