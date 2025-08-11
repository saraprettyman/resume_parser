from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.regex_helpers import find_first
from config.patterns import EMAIL_PATTERN, PHONE_PATTERN, LINKEDIN_PATTERN, GITHUB_PATTERN
import re

class ContactExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))

        # Improved name extraction:
        # - Must be on its own line
        # - Must be 2–4 words
        # - No @ or digits
        name_match = re.search(
            r'^(?!.*@)(?!.*\d)([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})$',
            text,
            re.MULTILINE
        )
        name = name_match.group(1).strip() if name_match else ""

        email = find_first(EMAIL_PATTERN, text)
        phone = find_first(PHONE_PATTERN, text)
        linkedin = find_first(LINKEDIN_PATTERN, text)
        github = find_first(GITHUB_PATTERN, text)

        # Additional URLs: exclude LinkedIn/GitHub & normalize
        all_urls = re.findall(r'(?:https?://|www\.)[^\s)]+', text)
        known_urls = set(filter(None, [linkedin, github]))
        additional_urls = [
            u.rstrip('/')
            for u in all_urls
            if u.rstrip('/') not in {ku.rstrip('/') for ku in known_urls}
        ]

        return {
            "name": name,
            "email": email or "",
            "phone": phone or "",
            "linkedin": linkedin or "",
            "github": github or "",
            "additional_urls": additional_urls
        }
