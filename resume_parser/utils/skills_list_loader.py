"""
skills_list_loader.py

This module provides utility functions for loading the predefined skills dataset
from a JSON file. The dataset contains both technical skills grouped by category
and mappings of job roles to relevant skill categories.

Functionality:
    - Load the complete skills dataset from a JSON file.
    - Retrieve a list of available roles defined in the dataset.

Typical Usage:
    from resume_parser.utils.skills_list_loader import load_skills, load_roles

    skills_data = load_skills()
    roles = load_roles()

Functions:
    load_skills(file_path: str | None) -> dict:
        Loads the full skills dataset from the specified JSON file or from the
        default path if none is provided.

    load_roles(file_path: str | None) -> list[str]:
        Retrieves a list of role names from the skills dataset.
"""

import json
import os

def load_skills(file_path=None):
    """
    Load the full skills dataset from a JSON file.

    If no file path is provided, this will attempt to load
    `data/skills_master.json` relative to the project root.

    Args:
        file_path (str, optional): Path to the skills JSON file.
            Defaults to None, in which case the default path is used.

    Returns:
        dict: The parsed JSON content, typically containing:
            - "ALL_TECHNICAL_SKILLS" (dict[str, list[dict]]):
                Mapping of category names to lists of skill definitions.
            - "ROLES" (dict[str, list[str]]):
                Mapping of role names to relevant skill categories.
    """

    if file_path is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))  # up from utils/
        file_path = os.path.join(base_dir, "data", "skills_master.json")

        file_path = os.path.abspath(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_roles(file_path=None):
    """
    Load the list of available role names from the skills dataset.

    Args:
        file_path (str, optional): Path to the skills JSON file.
            Defaults to None, in which case the default path is used.

    Returns:
        list[str]: A list of role names found under the "ROLES" key.
    """
    skills = load_skills(file_path)
    return list(skills.get("ROLES", {}).keys())
