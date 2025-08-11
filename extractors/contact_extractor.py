# extractors/contact_extractor.py
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.regex_helpers import find_first
from config.patterns import EMAIL_PATTERN, PHONE_PATTERN, LINKEDIN_PATTERN, GITHUB_PATTERN

class ContactExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        email = find_first(EMAIL_PATTERN, text)
        phone = find_first(PHONE_PATTERN, text)
        linkedin = find_first(LINKEDIN_PATTERN, text)
        github = find_first(GITHUB_PATTERN, text)
        return {
            "email": email or "",
            "phone": phone or "",
            "linkedin": linkedin or "",
            "github": github or ""
        }
