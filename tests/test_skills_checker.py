# pylint: disable=duplicate-code
"""Tests for SkillsChecker to ensure general skills are correctly extracted."""

from typing import Any
from resume_parser.utils.skills_checker import SkillsChecker


def test_general_skills_extraction(fake_resume_path: Any):
    """
    Validates that SkillsChecker correctly extracts key general skills
    from a fake resume file.
    """
    checker = SkillsChecker()
    skills = checker.extract_general_skills(str(fake_resume_path))

    # Flatten the found skills across all categories
    found_skills = {
        skill
        for category in skills.values()
        for skill in category["found"]
    }

    assert "Python" in found_skills, "'Python' should be detected in found skills"
    assert "AWS" in found_skills, "'AWS' should be detected in found skills"
    assert any(
        s.lower() == "machine learning" for s in found_skills
    ), "'machine learning' should be detected in found skills"
