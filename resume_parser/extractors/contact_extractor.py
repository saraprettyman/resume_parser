import re
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.regex_helpers import find_first, find_additional_urls
from config.patterns import (
    NAME_PATTERN, EMAIL_PATTERN, PHONE_PATTERN,
    LINKEDIN_PATTERN, GITHUB_PATTERN
)

class ContactExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))

        # Name (first match in the file that fits NAME_PATTERN)
        name_match = re.search(NAME_PATTERN, text, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else ""

        # Direct contact fields
        email = find_first(EMAIL_PATTERN, text) or ""
        phone = find_first(PHONE_PATTERN, text) or ""
        linkedin = find_first(LINKEDIN_PATTERN, text) or ""
        github = find_first(GITHUB_PATTERN, text) or ""

        # Other URLs (excluding LinkedIn & GitHub)
        additional_urls = find_additional_urls(text, [linkedin, github])

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "additional_urls": additional_urls
        }
