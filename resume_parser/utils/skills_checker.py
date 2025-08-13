import re
from resume_parser.utils.skills_list_loader import load_skills, load_roles


class SkillsChecker:
    """
    A utility class for extracting and matching skills from resume text
    against a predefined skills dataset.

    The skills dataset is expected to be loaded from a JSON file using
    `load_skills` and structured with two top-level keys:
      - "ALL_TECHNICAL_SKILLS": Mapping of skill categories to lists of skill definitions.
      - "ROLES": Mapping of role names to relevant skill categories.

    Typical workflow:
      1. Load the complete skills dataset upon initialization.
      2. Extract skills either from all categories (general) or for a specific role.
      3. Return results showing which skills were found and which were missing.
    """

    def __init__(self):
        """
        Initialize the SkillsChecker by loading the complete skills dataset.
        """
        self.skills_data = load_skills()

    def load_roles(self):
        """
        Retrieve the list of available roles from the skills dataset.

        Returns:
            list[str]: A list of role names.
        """
        return load_roles()

    def extract_general_skills(self, file_path: str):
        """
        Extract all technical skills (across all categories) from a resume.

        Args:
            file_path (str): Path to the resume file.

        Returns:
            dict: Mapping of category name to a dictionary with:
                - "found" (list[str]): Skills found in the resume.
                - "missing" (list[str]): Skills not found in the resume.
        """
        from resume_parser.utils.file_reader import read_resume
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted = {}

        for category, skills in self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).items():
            found, missing = self._match_skills(skills, resume_lower, resume_text)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path: str, role: str):
        """
        Extract technical skills relevant to a specific role from a resume.

        Args:
            file_path (str): Path to the resume file.
            role (str): Role name to extract relevant skills for.

        Returns:
            dict: Mapping of category name to a dictionary with:
                - "found" (list[str]): Skills found in the resume.
                - "missing" (list[str]): Skills not found in the resume.
        """
        from resume_parser.utils.file_reader import read_resume
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

        return extracted

    def _match_skills(self, skills, resume_lower, resume_text):
        """
        Match a list of skills against the normalized resume text.

        Matching is case-insensitive and uses word boundaries to ensure
        whole-word matches. Aliases for each skill are also considered.

        Args:
            skills (list[dict]): List of skill definitions, each containing:
                - "name" (str): Primary skill name.
                - "aliases" (list[str], optional): Alternative names for the skill.
            resume_lower (str): Lowercase version of the resume text.
            resume_text (str): Original resume text (currently unused, but kept for potential future matching rules).

        Returns:
            tuple[list[str], list[str]]:
                - found: Skills matched in the resume.
                - missing: Skills not found in the resume.
        """
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
