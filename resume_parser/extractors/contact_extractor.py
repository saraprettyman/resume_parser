import re
from resume_parser.extractors.base_extractor import BaseExtractor
from resume_parser.utils.file_reader import read_resume
from resume_parser.utils.regex_helpers import find_first, find_additional_urls
from resume_parser.config.patterns import (
    NAME_PATTERN, EMAIL_PATTERN, PHONE_PATTERN,
    LINKEDIN_PATTERN, GITHUB_PATTERN
)

class ContactExtractor(BaseExtractor):
    """
    Extracts contact information from a resume.

    This extractor identifies and returns the candidate's:
    - Name
    - Email address
    - Phone number
    - LinkedIn profile URL
    - GitHub profile URL
    - Any additional URLs (excluding LinkedIn and GitHub)

    Data is extracted by matching text against predefined regex patterns
    from `config.patterns`.

    Methods
    -------
    extract(file_path: str) -> dict
        Reads the resume file, normalizes its text, and extracts
        contact details as a dictionary.
    """

    def extract(self, file_path: str) -> dict:
        """
        Extract contact information from the provided resume file.

        Parameters
        ----------
        file_path : str
            Path to the resume file.

        Returns
        -------
        dict
            A dictionary containing:
            - name (str): Candidate's name.
            - email (str): Email address.
            - phone (str): Phone number.
            - linkedin (str): LinkedIn profile URL.
            - github (str): GitHub profile URL.
            - additional_urls (list[str]): Any other URLs found in the resume,
              excluding LinkedIn and GitHub.
        """
        text = self.normalize(read_resume(file_path))

        # Name (first match that fits NAME_PATTERN)
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
