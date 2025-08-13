from resume_parser.utils.skills_checker import SkillsChecker


def test_general_skills_extraction(fake_resume_path):
    checker = SkillsChecker()
    skills = checker.extract_general_skills(str(fake_resume_path))

    # Flatten the "found" skills from all categories
    found_skills = {skill for category in skills.values() for skill in category["found"]}

    assert "Python" in found_skills
    assert "AWS" in found_skills
    assert any(s.lower() == "machine learning" for s in found_skills)
