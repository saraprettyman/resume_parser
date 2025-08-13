"""Tests for the EducationExtractor, ensuring educational history is correctly parsed."""

from typing import Any
from resume_parser.extractors.education_extractor import EducationExtractor


def test_education_extraction(fake_resume_path: Any):
    """
    Validates that EducationExtractor can parse educational entries
    with required fields from a fake resume.
    """
    extractor = EducationExtractor()
    results = extractor.extract(str(fake_resume_path))

    # Structure validation
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "items" in results, "'items' key missing from results"
    assert isinstance(results["items"], list), "'items' should be a list"
    assert results["items"], "'items' list should not be empty"

    # Validate first education entry
    edu_entry = results["items"][0]
    assert any(
        keyword in edu_entry["Degree & Emphasis"].lower()
        for keyword in ["bachelor", "master", "associate", "ph.d", "doctor"]
    ), "Degree & Emphasis should contain a valid degree keyword"
    assert edu_entry["Institution"], "Institution should not be empty"
    assert edu_entry["Graduation Date"], "Graduation Date should not be empty"
