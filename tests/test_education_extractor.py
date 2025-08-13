from resume_parser.extractors.education_extractor import EducationExtractor

def test_education_extraction(fake_resume_path):
    extractor = EducationExtractor()
    results = extractor.extract(str(fake_resume_path))

    assert isinstance(results, dict)
    assert "items" in results
    assert isinstance(results["items"], list)
    assert len(results["items"]) > 0

    edu_entry = results["items"][0]
    assert any(keyword in edu_entry["Degree & Emphasis"].lower()
               for keyword in ["bachelor", "master", "associate", "ph.d", "doctor"])
    # We don't hardcode Springfield University since fakes will vary
    assert edu_entry["Institution"]
    assert edu_entry["Graduation Date"]
