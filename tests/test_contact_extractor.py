"""Tests for the ContactExtractor, ensuring basic contact fields are parsed correctly."""

from typing import Any
from resume_parser.extractors.contact_extractor import ContactExtractor


def test_contact_extraction(fake_resume_path: Any):
    """
    Validates that ContactExtractor can parse key contact information
    from the given fake resume file.
    """
    extractor = ContactExtractor()
    results = extractor.extract(str(fake_resume_path))

    # Required keys must be present
    for key in ["name", "email", "phone", "linkedin", "github", "additional_urls"]:
        assert key in results, f"Missing expected key: {key}"

    # Field type and format checks
    assert isinstance(results["additional_urls"], list), "additional_urls must be a list"
    assert results["name"], "Name should not be empty"
    assert "@" in results["email"], "Email must contain @"
    assert results["phone"], "Phone number should not be empty"
