import re

def skill_in_text(skill, text):
    """Check if skill appears as a whole word/phrase in text."""
    # Escape special regex chars in skill, match whole word boundaries
    pattern = r'\b' + re.escape(skill) + r'\b'
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def extract_role_skills(resume_text, skills_dict, role):
    """Match resume text against skills for a specific role."""
    found_skills = set()
    roles_dict = skills_dict.get("ROLES", {})
    role_data = roles_dict.get(role, {})

    for category, skills in role_data.items():
        # Only iterate if the category actually contains a list
        if isinstance(skills, list):
            for skill in skills:
                if skill_in_text(skill, resume_text):
                    found_skills.add(skill)

    return sorted(found_skills)


def extract_all_technical_skills(resume_text, skills_dict):
    """Match resume text against ALL_TECHNICAL_SKILLS list."""
    found_skills = set()
    categories = skills_dict.get("ALL_TECHNICAL_SKILLS", {})

    for category, skills in categories.items():
        for skill in skills:
            if skill_in_text(skill, resume_text):
                found_skills.add(skill)

    return sorted(found_skills)


def extract_certifications(resume_text, skills_dict, role=None):
    """Match resume text against certifications (general or role-specific)."""
    found_certs = set()

    # Role-specific certifications
    if role:
        roles_dict = skills_dict.get("ROLES", {})
        role_data = roles_dict.get(role, {})
        role_certs = role_data.get("Certifications", [])
        for cert in role_certs:
            if skill_in_text(cert, resume_text):
                found_certs.add(cert)

    # General certifications
    certifications = skills_dict.get("CERTIFICATIONS", [])
    for cert in certifications:
        if skill_in_text(cert, resume_text):
            found_certs.add(cert)

    return sorted(found_certs)
