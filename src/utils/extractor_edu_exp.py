# src/utils/extractor_edu_exp.py
import re
from rich.table import Table
from rich.console import Console
from .file_reader import read_resume

console = Console()

class ATSEducationExperienceExtractor:
    def __init__(self):
        # Recognize common section headers (case-insensitive)
        self.section_patterns = [
            r"professional\s+summary",
            r"summary",
            r"profile",
            r"experience",
            r"work\s+history",
            r"employment\s+history",
            r"projects?",
            r"skills?",
            r"education",
            r"certifications?",
            r"awards?",
            r"publications?"
        ]

        # month names for date detection
        self.months_regex = (
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        )
        self.month_year = rf"{self.months_regex}\s+\d{{4}}"
        # date ranges: "May 2020 - Present", "May 2020 – Aug 2021", "2020 - 2021", "2020 - Present"
        self.date_range = (
            rf"(?:{self.month_year}\s*[-–]\s*(?:{self.month_year}|Present|\b\d{{4}}\b)|"
            rf"\b\d{{4}}\b\s*[-–]\s*(?:\d{{4}}|Present)|"
            rf"{self.month_year}|\b\d{{4}}\b|Present)"
        )

        # degree and GPA detection
        self.degree_pattern = re.compile(
            r"(Bachelor(?:'s)?(?:\s+of)?[^\n,;]*)|"
            r"(Master(?:'s)?(?:\s+of)?[^\n,;]*)|"
            r"(Ph\.?D\.?|Doctorate(?:\s+in)?[^\n,;]*)|"
            r"(Associate(?:'s)?(?:\s+of)?[^\n,;]*)|"
            r"(High\s+School\s+Diploma|GED|Diploma|Certificate)",
            re.IGNORECASE
        )
        self.gpa_pattern = re.compile(
            r"\bGPA\b[:\s]*([0-4](?:[.,]\d{1,2})?)(?:\s*/\s*([0-4](?:[.,]\d{1,2})?))?",
            re.IGNORECASE
        )

    # ----------------------
    # Public API
    # ----------------------
    def extract_edu_exp(self, file_path):
        """
        Return a dictionary keyed by section name (Title Case).
        Each section: { "status": "Found"/"Missing", "value": full_text, "items": [ ...structured items...] }
        """
        raw = read_resume(file_path) or ""
        text = self._normalize_text(raw)

        sections = self._split_into_sections(text)

        # ensure canonical section names in results
        canonical = ["Professional Summary", "Profile", "Skills", "Experience", "Projects", "Education", "Certifications", "Awards", "Publications"]
        results = {}
        for name in canonical:
            key_lower = name.lower()
            # find if we matched a header variant
            content = sections.get(name, "")
            # also accept single-word synonyms (Summary->Professional Summary etc.)
            if not content:
                # try to match by lower-case header keys in sections
                for k, v in sections.items():
                    if k.lower() == name.lower():
                        content = v
                        break
            status = "Found" if content.strip() else "Missing"

            items = []
            if status == "Found":
                if name == "Experience":
                    items = self._parse_experience(content)
                elif name == "Projects":
                    items = self._parse_projects(content)
                elif name == "Education":
                    items = self._parse_education(content)
                else:
                    # leave other sections as raw text
                    items = []

            results[name] = {
                "status": status,
                "value": content,
                "items": items
            }

        # include any other discovered headers not in canonical list
        for k, v in sections.items():
            if k not in results:
                results[k] = {"status": "Found" if v.strip() else "Missing", "value": v, "items": []}

        return results

    def display_edu_exp_table(self, results, show_gpa=False, show_edu_type=False):
        """
        Accepts the output of extract_edu_exp and prints nice Rich tables.
        show_gpa / show_edu_type control whether GPA & degree type columns are shown for Education.
        """
        # Print Professional Summary / Profile (if present)
        for header in ["Professional Summary", "Profile", "Skills"]:
            sec = results.get(header)
            if sec and sec["status"] == "Found":
                panel_tbl = Table(title=header, show_lines=True, expand=True)
                panel_tbl.add_column("Extracted Text", style="white")
                panel_tbl.add_row(sec["value"][:1000] + ("..." if len(sec["value"]) > 1000 else ""))
                console.print(panel_tbl)

        # Experience
        exp = results.get("Experience", {"items": [], "value": ""})
        if exp["items"]:
            tbl = Table(title="Experience", show_lines=True, expand=True)
            tbl.add_column("Job Title", style="bold cyan")
            tbl.add_column("Company", style="cyan")
            tbl.add_column("Start Date", style="white")
            tbl.add_column("End Date", style="white")
            tbl.add_column("Details", style="white")
            for it in exp["items"]:
                details = ""
                if it.get("Bullets"):
                    # join bullets to multi-line string
                    details = "\n".join(f"• {b}" for b in it["Bullets"])
                else:
                    details = it.get("Details", "")
                tbl.add_row(it.get("Job Title", ""), it.get("Company", ""), it.get("Start Date", ""), it.get("End Date", ""), details)
            console.print(tbl)
        else:
            # fallback: print raw experience text if present
            if exp["value"]:
                tbl = Table(title="Experience", show_lines=True, expand=True)
                tbl.add_column("Extracted Text")
                tbl.add_row(exp["value"][:1000] + ("..." if len(exp["value"]) > 1000 else ""))
                console.print(tbl)

        # Projects
        proj = results.get("Projects", {"items": [], "value": ""})
        if proj["items"]:
            tbl = Table(title="Projects", show_lines=True, expand=True)
            tbl.add_column("Project", style="bold cyan")
            tbl.add_column("Dates", style="cyan")
            tbl.add_column("Details", style="white")
            for it in proj["items"]:
                details = "\n".join(f"• {b}" for b in it.get("Bullets", [])) if it.get("Bullets") else it.get("Details", "")
                tbl.add_row(it.get("Project", ""), it.get("Dates", ""), details)
            console.print(tbl)
        else:
            if proj["value"]:
                tbl = Table(title="Projects", show_lines=True, expand=True)
                tbl.add_column("Extracted Text")
                tbl.add_row(proj["value"][:1000] + ("..." if len(proj["value"]) > 1000 else ""))
                console.print(tbl)

        # Education
        edu = results.get("Education", {"items": [], "value": ""})
        if edu["items"]:
            # configure columns depending on flags
            tbl = Table(title="Education", show_lines=True, expand=True)
            tbl.add_column("Institution", style="bold cyan")
            tbl.add_column("Graduation Date", style="white")
            if show_edu_type:
                tbl.add_column("Degree", style="cyan")
            if show_gpa:
                tbl.add_column("GPA", style="white")
            tbl.add_column("Details", style="white")

            for it in edu["items"]:
                row = [it.get("Institution", ""), it.get("Graduation Date", "")]
                if show_edu_type:
                    row.append(it.get("Degree", ""))
                if show_gpa:
                    row.append(it.get("GPA", ""))
                # details / bullets
                details = "\n".join(f"• {b}" for b in it.get("Bullets", [])) if it.get("Bullets") else it.get("Details", "")
                row.append(details)
                tbl.add_row(*row)
            console.print(tbl)
        else:
            if edu["value"]:
                tbl = Table(title="Education", show_lines=True, expand=True)
                tbl.add_column("Extracted Text")
                tbl.add_row(edu["value"][:1000] + ("..." if len(edu["value"]) > 1000 else ""))
                console.print(tbl)

    # ----------------------
    # Internal helpers
    # ----------------------
    def _normalize_text(self, text):
        if text is None:
            return ""
        # preserve paragraphs; standardize newlines and reduce excessive blank lines
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # trim trailing/leading spaces on each line
        lines = [ln.rstrip() for ln in text.split("\n")]
        # remove leading/trailing empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        # collapse 3+ blank lines into 2
        normalized = []
        blank_count = 0
        for ln in lines:
            if not ln.strip():
                blank_count += 1
                if blank_count <= 2:
                    normalized.append("")
            else:
                blank_count = 0
                normalized.append(ln)
        return "\n".join(normalized).strip()

    def _split_into_sections(self, text):
        """
        Find headers (at start of line) and cut the text into sections.
        Returns a dict mapping Title Case header -> content.
        """
        if not text:
            return {}

        # Build header alternation and anchor to line-start
        hdr_alt = "|".join(self.section_patterns)
        # match header on its own line (allow trailing ":" or "-" or whitespace)
        pat = re.compile(rf"(?mi)^\s*(?P<header>(?:{hdr_alt}))\s*[:\-–—]?\s*$")
        matches = list(pat.finditer(text))

        sections = {}
        if not matches:
            # fallback: attempt to extract major sections by searching keywords
            for key in ["Education", "Experience", "Projects", "Skills", "Professional Summary", "Profile"]:
                m = re.search(rf"(?si){key}\s*[:\-–—]?\s*(.*?)(?=(?:\n[A-Z][^\n]*\n)|$)", text)
                if m:
                    sections[key] = m.group(1).strip()
            # if still empty, return whole text as "Document"
            if not sections:
                sections["Document"] = text
            return sections

        # use matches to slice the document
        for i, m in enumerate(matches):
            header = m.group("header").strip().title()
            start = m.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(text)
            content = text[start:end].strip()
            # normalize header names (Projects vs Project) -> Projects
            if header.lower().startswith("project"):
                header = "Projects"
            elif header.lower().startswith("work") or header.lower().startswith("employment"):
                header = "Experience"
            elif header.lower().startswith("professional") or header.lower() == "summary" or header.lower() == "profile":
                header = "Professional Summary" if header.lower().startswith("professional") else header.title()
            elif header.lower().startswith("education"):
                header = "Education"
            elif header.lower().startswith("skills"):
                header = "Skills"
            sections[header] = content

        return sections

    def _parse_experience(self, content):
        """
        Split the Experience section into blocks and attempt to extract:
        - Job Title
        - Company
        - Start Date / End Date
        - Bullets or Details
        """
        items = []
        if not content.strip():
            return items

        # Split into blocks by 1+ blank lines (preserves paragraphs under each job)
        blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]
        for block in blocks:
            # find dates if present anywhere in block
            date_match = re.search(self.date_range, block, re.IGNORECASE)
            date_str = date_match.group(0).strip() if date_match else ""
            # split start/end if possible
            start_date, end_date = "", ""
            if date_str:
                # normalize dash characters
                dclean = re.sub(r"[–—]", "-", date_str)
                if "-" in dclean:
                    parts = [p.strip() for p in dclean.split("-", 1)]
                    start_date, end_date = parts[0], parts[1]
                else:
                    start_date = dclean

            # split lines and infer title/company
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            title_line = lines[0] if lines else ""
            # remove date string from title_line if it was appended there
            if date_str and date_str in title_line:
                title_line = title_line.replace(date_str, "").strip()

            # attempt to split title/company using common separators
            split_sep = re.split(r"\s+(?:@| at | - | — | – | \| )\s+", title_line, maxsplit=1, flags=re.IGNORECASE)
            if len(split_sep) >= 2:
                job_title = split_sep[0].strip()
                company = split_sep[1].strip()
            else:
                # sometimes company is on second line
                if len(lines) > 1 and re.search(r"(Inc|LLC|Corp|Company|Co\.|Ltd|LLP|LLC|University|Institute|School|Labs|Systems)", lines[1], re.IGNORECASE):
                    job_title = title_line
                    company = lines[1]
                    # remove the second line from details later
                    detail_lines = lines[2:]
                else:
                    # fallback: entire first line is job title
                    job_title = title_line
                    company = ""

                    detail_lines = lines[1:]

            # If split_sep gave company, set detail_lines accordingly
            if len(split_sep) >= 2:
                detail_lines = lines[1:]

            # remove any lines that are just date lines from details
            # also remove lines that look like locations only (City, State)
            filtered = []
            for ln in detail_lines:
                if re.search(self.date_range, ln, re.IGNORECASE):
                    continue
                if re.fullmatch(r"[A-Za-z .]+,\s*[A-Za-z]{2,}", ln):
                    continue
                filtered.append(ln)

            # extract bullets (lines starting with bullet chars) and normal details
            bullets = []
            free_text_lines = []
            for ln in filtered:
                m = re.match(r"^[\u2022\-\*\•\•\s]{1,4}(.*)$", ln)
                if m:
                    b = m.group(1).strip()
                    if b:
                        bullets.append(b)
                else:
                    free_text_lines.append(ln)

            details_text = "\n".join(free_text_lines).strip()

            items.append({
                "Job Title": job_title,
                "Company": company,
                "Start Date": start_date,
                "End Date": end_date,
                "Details": details_text,
                "Bullets": bullets
            })

        return items

    def _parse_projects(self, content):
        items = []
        if not content.strip():
            return items

        blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]
        for block in blocks:
            # find a date if present in block (optional)
            date_match = re.search(self.date_range, block, re.IGNORECASE)
            dates = date_match.group(0).strip() if date_match else ""
            # project title likely on first line
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            proj_title = lines[0] if lines else ""
            # remove date from title if appended
            if dates and dates in proj_title:
                proj_title = proj_title.replace(dates, "").strip()
            # details and bullets
            detail_lines = lines[1:]
            bullets = []
            free_lines = []
            for ln in detail_lines:
                m = re.match(r"^[\u2022\-\*\•\s]{1,4}(.*)$", ln)
                if m:
                    b = m.group(1).strip()
                    if b:
                        bullets.append(b)
                else:
                    free_lines.append(ln)
            details_text = "\n".join(free_lines).strip()
            items.append({
                "Project": proj_title,
                "Dates": dates,
                "Details": details_text,
                "Bullets": bullets
            })
        return items

    def _parse_education(self, content):
        items = []
        if not content.strip():
            return items

        # split blocks by double-newline
        blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]

        for block in blocks:
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            # institution detection: prefer lines containing University/College/Institute/School/Academy
            institution = ""
            grad_date = ""
            degree = ""
            gpa = ""
            details_lines = []

            # find grad date anywhere (month-year or year)
            date_match = re.search(self.month_year, block, re.IGNORECASE)
            if not date_match:
                # fallback to year-only
                year_match = re.search(r"\b(19|20)\d{2}\b", block)
                if year_match:
                    grad_date = year_match.group(0)
            else:
                grad_date = date_match.group(0)

            # find GPA
            gpa_match = self.gpa_pattern.search(block)
            if gpa_match:
                gpa_main = gpa_match.group(1).replace(",", ".")
                if gpa_match.group(2):
                    gpa = f"{gpa_main}/{gpa_match.group(2).replace(',', '.')}"
                else:
                    gpa = gpa_main

            # find degree
            deg_match = self.degree_pattern.search(block)
            if deg_match:
                degree = deg_match.group(0).strip()

            # find institution from lines
            for ln in lines:
                if re.search(r"(University|College|Institute|School|Academy|School of)", ln, re.IGNORECASE):
                    institution = ln
                    # remaining lines after institution are details
                    idx = lines.index(ln)
                    details_lines = lines[idx+1:]
                    break
            if not institution:
                # fallback: first line is likely institution or degree+institution
                if lines:
                    institution = lines[0]
                    details_lines = lines[1:]

            # Clean details_lines: remove any that are just date or GPA lines
            cleaned = []
            for ln in details_lines:
                if re.search(self.month_year, ln, re.IGNORECASE) or re.search(r"\b(19|20)\d{2}\b", ln):
                    continue
                if self.gpa_pattern.search(ln):
                    continue
                cleaned.append(ln)

            # extract bullets from cleaned
            bullets = []
            free_text = []
            for ln in cleaned:
                m = re.match(r"^[\u2022\-\*\•\s]{1,4}(.*)$", ln)
                if m:
                    val = m.group(1).strip()
                    if val:
                        bullets.append(val)
                else:
                    free_text.append(ln)

            details_text = "\n".join(free_text).strip()

            items.append({
                "Institution": institution,
                "Graduation Date": grad_date,
                "Degree": degree,
                "GPA": gpa,
                "Details": details_text,
                "Bullets": bullets
            })

        return items
