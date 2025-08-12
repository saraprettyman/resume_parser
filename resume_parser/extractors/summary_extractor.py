# extractors/summary_extractor.py
from .base_extractor import BaseExtractor
from utils.section_finder import find_section
from config.patterns import SUMMARY_START, SUMMARY_END
from .base_extractor import BaseExtractor
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume

class SummaryExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        section = find_section(text, SUMMARY_START, SUMMARY_END)
        return {"section": section}
