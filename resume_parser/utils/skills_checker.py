"""
skills_checker.py

This module defines the SkillsChecker class, responsible for extracting and
matching technical skills from resume text against a predefined dataset.

Functionality:
    - Loads a comprehensive skills dataset from JSON via `load_skills`.
    - Retrieves role definitions and their associated skill categories.
    - Extracts all technical skills present in a resume.
    - Extracts role-specific technical skills from a resume.
    - Matches skills (including aliases) in a case-insensitive manner.

Classes:
    SkillsChecker:
        Provides methods for:
            - extract_general_skills(file_path): Extracts all skills across categories.
            - extract_role_skills(file_path, role): Extracts skills for a specific role.
            - load_roles(): Returns a list of available roles.
"""

import re
from typing import Any, Dict, List, Tuple

from resume_parser.utils.skills_list_loader import load_skills, load_roles
from resume_parser.utils.file_reader import read_resume


class SkillsChecker:  # pylint: disable=too-few-public-methods
    """
    A utility class for extracting and matching skills from resume text
    against a predefined skills dataset.

    The skills dataset is loaded from JSON using `load_skills` and includes:
      - "ALL_TECHNICAL_SKILLS": category -> skill definitions
      - "ROLES": role -> list of categories
    """

    def __init__(self) -> None:
        """Initialize the SkillsChecker by loading the complete skills dataset."""
        self.skills_data = load_skills()

    @staticmethod
    def load_roles() -> List[str]:
        """
        Retrieve the list of available roles.

        Returns:
            list[str]: Role names.
        """
        return load_roles()

    def extract_general_skills(self, file_path: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract all technical skills (across all categories) from a resume.
        """
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        extracted: Dict[str, Dict[str, List[str]]] = {}

        for category, skills in self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).items():
            found, missing = self._match_skills(skills, resume_lower)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    def extract_role_skills(self, file_path: str, role: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract technical skills relevant to a specific role from a resume.
        """
        resume_text = read_resume(file_path)
        resume_lower = resume_text.lower()
        role_categories = self.skills_data.get("ROLES", {}).get(role, [])
        extracted: Dict[str, Dict[str, List[str]]] = {}

        for category in role_categories:
            skills = self.skills_data.get("ALL_TECHNICAL_SKILLS", {}).get(category, [])
            found, missing = self._match_skills(skills, resume_lower)
            extracted[category] = {"found": found, "missing": missing}

        return extracted

    @staticmethod
    def _match_skills(skills: List[Dict[str, Any]],
                      resume_lower: str) -> Tuple[List[str], List[str]]:
        """
        Match a list of skills against lowercase resume text.
        """
        found: List[str] = []
        missing: List[str] = []
        for skill in skills:
            skill_names = ([skill["name"].lower()]
                           + [alias.lower() for alias in skill.get("aliases", [])])
            if any(re.search(rf"\b{re.escape(name)}\b", resume_lower) for name in skill_names):
                found.append(skill["name"])
            else:
                missing.append(skill["name"])
        return found, missing
