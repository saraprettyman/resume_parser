# skills_checker/skills_checker.py
import re
from utils.skills_list_loader import load_skills, load_roles

class SkillsChecker:
    def __init__(self):
        self.skills_data = load_skills()

    def load_roles(self):
        return load_roles()

    def extract_general_skills(self, file_path: str):
        from utils.file_reader import read_resume
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted = {}

        for category, skills in self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).items():
            found, missing = self._match_skills(skills, resume_lower, resume_text)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path: str, role: str):
        from utils.file_reader import read_resume
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        role_categories = self.skills_data.get("ROLES", {}).get(role, [])
        extracted = {}
        total_skills, matched_skills = 0, 0

        for category in role_categories:
            skills = self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).get(category, [])
            total_skills += len(skills)
            found, missing = self._match_skills(skills, resume_lower, resume_text)
            matched_skills += len(found)
            extracted[category] = {"found": found, "missing": missing}

        score = round((matched_skills / total_skills) * 100, 2) if total_skills else 0
        return extracted, score

    def _match_skills(self, skills, resume_lower, resume_text):
        found, missing = [], []
        for skill in skills:
            skill_names = [skill["name"].lower()] + [alias.lower() for alias in skill.get("aliases", [])]
            matched = False
            for s in skill_names:
                if re.search(rf"\b{re.escape(s)}\b", resume_lower):
                    found.append(skill["name"])
                    matched = True
                    break
            if not matched:
                missing.append(skill["name"])
        return found, missing
