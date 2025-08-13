"""
summary_extractor.py

Contains the SummaryExtractor class, which identifies and extracts
the 'Summary' section from a resume using pre-defined start and end
regex patterns.
"""

from resume_parser.extractors.base_extractor import BaseExtractor
from resume_parser.utils.section_finder import find_section
from resume_parser.config.patterns import SUMMARY_START, SUMMARY_END
from resume_parser.utils.file_reader import read_resume


class SummaryExtractor(BaseExtractor):  # pylint: disable=too-few-public-methods
    """
    Extractor for the 'Summary' section of a resume.

    Inherits from:
        BaseExtractor: Provides normalization and shared extraction utilities.

    Methods:
        extract(file_path: str) -> dict:
            Reads a resume, normalizes its text, and extracts the summary section
            using pre-defined start and end patterns.
    """

    def extract(self, file_path: str) -> dict:
        """
        Extract the Summary section from the given resume file.

        Args:
            file_path (str): Path to the resume file.

        Returns:
            dict: A dictionary containing:
                - "section" (str): The extracted summary text. If no section
                  is found, returns an empty string.
        """
        text = self.normalize(read_resume(file_path))
        section = find_section(text, SUMMARY_START, SUMMARY_END)
        return {"section": section}
