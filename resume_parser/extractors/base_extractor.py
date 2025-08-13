# extractors/base_extractor.py
from abc import ABC, abstractmethod
from resume_parser.utils.text_normalizer import normalize_whitespace

class BaseExtractor(ABC):
    """
    Abstract base class for all resume data extractors.
    Each extractor handles parsing a specific type of resume section
    (e.g., experience, education, contact info).
    """

    def normalize(self, text: str) -> str:
        """
        Normalize whitespace in the given text.

        Args:
            text (str): Input text from the resume.

        Returns:
            str: Cleaned text with consistent spacing.
        """
        return normalize_whitespace(text or "")

    @abstractmethod
    def extract(self, file_path: str) -> dict:
        """
        Abstract method to extract structured data from a resume file.

        Args:
            file_path (str): Path to the resume file.

        Returns:
            dict: Extracted structured data (format depends on subclass).
        """
        raise NotImplementedError
