# extractors/skills_extractor.py
from .base_extractor import BaseExtractor
from utils.file_reader import read_resume
from utils.skills_list_loader import load_skills
import re

class SkillsExtractor(BaseExtractor):
    def __init__(self):
        self.skills_data = load_skills()

    def extract(self, file_path: str) -> dict:
        text = self.normalize(read_resume(file_path))
        text_lower = text.lower()
        extracted = {}

        for category, skills in self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).items():
            found, missing = self._match_skills(skills, text_lower, text)
            extracted[category] = {"found": found, "missing": missing}

        # Also return the raw skills section if present
        return {"section": text, "skills_check": extracted}

    def _match_skills(self, skills, resume_lower, resume_text):
        found, missing = [], []
        for skill in skills:
            skill_names = [skill["name"].lower()] + [alias.lower() for alias in skill.get("aliases", [])]
            matched = False
            for s in skill_names:
                # word boundary match
                if re.search(rf"\b{re.escape(s)}\b", resume_lower):
                    found.append(skill["name"])
                    matched = True
                    break
            if not matched:
                missing.append(skill["name"])
        return found, missing
