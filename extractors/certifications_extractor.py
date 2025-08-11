# extractors/certifications_extractor.py
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.skills_list_loader import load_skills
import re

class CertificationsExtractor(BaseExtractor):
    """
    Certifications may be stored in the skills_master JSON (CERTIFICATIONS or similar)
    or appear in resume text; this extractor returns certifications found in skills JSON
    and those directly present in the resume text.
    """
    def __init__(self):
        self.skills_data = load_skills()

    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        text_lower = text.lower()
        certs_from_list = self.skills_data.get("CERTIFICATIONS", [])
        found = []
        for c in certs_from_list:
            name = c if isinstance(c, str) else c.get("name", "")
            if name and name.lower() in text_lower:
                found.append(name)
        # Also attempt to find lines in a certifications block
        # naive extraction: split lines and keep those containing keywords "cert" or known vendor names
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        inline_found = []
        for ln in lines:
            if re.search(r"certificat|certification|certified|certificate", ln, re.IGNORECASE):
                inline_found.append(ln)
        # unify and dedupe
        combined = list(dict.fromkeys(found + inline_found))
        return {"section": text, "certifications": combined}
