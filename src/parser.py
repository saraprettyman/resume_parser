import os
from collections import Counter
from typing import Dict, Any
from .utils.file_reader import read_pdf, read_docx
from .utils.skills_loader import load_skills


def extract_skills(text: str, skills_dict: Dict[str, list]) -> Dict[str, Dict[str, int]]:
    """
    Match known skills from the skills dictionary and count occurrences, grouped by category.

    Args:
        text (str): Resume text.
        skills_dict (dict): {category: [skills]}.

    Returns:
        dict: {category: {skill: count}} for all skills found.
    """
    lower_text = text.lower()
    category_counts = {}

    for category, skills in skills_dict.items():
        found_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            count = lower_text.count(skill_lower)
            if count > 0:
                found_skills.extend([skill] * count)  # multiple entries for counting
        if found_skills:
            category_counts[category] = dict(Counter(found_skills))

    return category_counts


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file (.pdf or .docx) and extract skills.

    Args:
        file_path (str): Path to resume file.

    Returns:
        dict: { 'file': file_path, 'skills': {category: {skill: count}} }
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = read_pdf(file_path)
    elif ext == ".docx":
        text = read_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Use .pdf or .docx.")

    skills_dict = load_skills()
    skills_found = extract_skills(text, skills_dict)

    return {
        "file": file_path,
        "skills": skills_found
    }
