# extractors/base_extractor.py
from abc import ABC, abstractmethod
from utils.text_normalizer import normalize_whitespace

class BaseExtractor(ABC):
    def normalize(self, text: str) -> str:
        return normalize_whitespace(text or "")

    @abstractmethod
    def extract(self, file_path: str) -> dict:
        """Extract structured data from a resume file path."""
        raise NotImplementedError
