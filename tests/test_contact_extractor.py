from resume_parser.extractors.contact_extractor import ContactExtractor

def test_contact_extraction(fake_resume_path):
    extractor = ContactExtractor()
    results = extractor.extract(str(fake_resume_path))

    # Required keys
    for key in ["name", "email", "phone", "linkedin", "github", "additional_urls"]:
        assert key in results

    assert isinstance(results["additional_urls"], list)
    assert results["name"]  # Make sure a name is extracted
    assert "@" in results["email"]
    assert results["phone"]