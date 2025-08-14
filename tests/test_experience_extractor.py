"""Tests for the ExperienceExtractor, ensuring work history is correctly parsed."""

from typing import Any
from resume_parser.extractors.experience_extractor import ExperienceExtractor


def test_experience_extraction(fake_resume_path: Any):
    """
    Validates that ExperienceExtractor can parse work experience entries
    with required fields from a fake resume.
    """
    extractor = ExperienceExtractor()
    results = extractor.extract(str(fake_resume_path))

    # Structure validation
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "items" in results, "'items' key missing from results"
    assert isinstance(results["items"], list), "'items' should be a list"
    assert results["items"], "'items' list should not be empty"

    # Validate first work experience entry
    first_exp = results["items"][0]
    for key in ["Company", "Job Title", "Start Date", "End Date"]:
        assert key in first_exp, f"'{key}' key missing from first experience entry"
