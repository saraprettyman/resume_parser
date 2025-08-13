from resume_parser.extractors.experience_extractor import ExperienceExtractor

def test_experience_extraction(fake_resume_path):
    extractor = ExperienceExtractor()
    results = extractor.extract(str(fake_resume_path))

    # The extractor always returns a dict with section and items
    assert isinstance(results, dict)
    assert "items" in results
    assert isinstance(results["items"], list)
    assert len(results["items"]) >= 1

    first_exp = results["items"][0]

    # Match actual keys from ExperienceExtractor
    assert "Company" in first_exp
    assert "Job Title" in first_exp
    assert "Start Date" in first_exp
    assert "End Date" in first_exp

    # Bullets should contain AWS or Python somewhere
    assert any(
        "AWS" in bullet or "Python" in bullet
        for bullet in first_exp.get("Bullets", [])
    )
