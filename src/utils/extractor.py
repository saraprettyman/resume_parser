import json
import re
from pathlib import Path

class ResumeSkillExtractor:
    def __init__(self):
        self.skills_master = self._load_skills_master()

    def _load_skills_master(self):
        """
        Load skills_master.json from a fixed relative path.
        """
        try:
            skills_file = Path(__file__).resolve().parent.parent / "data" / "skills_master.json"
            if not skills_file.exists():
                raise FileNotFoundError(f"skills_master.json not found at {skills_file}")

            with open(skills_file, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            print(f"[ERROR] Failed to load skills_master.json: {e}")
            return {"general": {}, "roles": {}}

    def extract_general_skills(self, resume_text):
        """
        Match skills from the 'general' section of skills_master.json against resume text.
        """
        found_skills = {}
        for category, skills in self.skills_master.get("general", {}).items():
            matched = [skill for skill in skills if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.IGNORECASE)]
            found_skills[category] = matched
        return found_skills

    def extract_role_specific(self, resume_text, role_name):
        """
        Match skills from a specific role in skills_master.json against resume text.
        Returns a dict with 'present' and 'missing' skill lists.
        """
        role_data = self.skills_master.get("roles", {}).get(role_name, {})
        present, missing = {}, {}

        for category, skills in role_data.items():
            matched = [skill for skill in skills if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.IGNORECASE)]
            present[category] = matched
            missing[category] = [skill for skill in skills if skill not in matched]

        return {"present": present, "missing": missing}
