from collections import Counter

def extract_skills(resume_text, role, skills_dict):
    """
    Extract skills relevant to a specific role.
    """
    lower_text = resume_text.lower()
    found = {}

    if role not in skills_dict:
        return {}

    for category, skills in skills_dict[role].items():
        found_in_category = []
        for skill in skills:
            if skill.lower() in lower_text:
                found_in_category.append(skill)
        if found_in_category:
            found[category] = sorted(set(found_in_category))

    return found


def extract_all_technical_skills(resume_text, skills_dict):
    """
    Extract all technical skills from any role/category (merged, no duplicates).
    """
    lower_text = resume_text.lower()
    found = {}

    for role, categories in skills_dict.items():
        if not isinstance(categories, dict):
            continue  # in case some global skills exist
        for category, skills in categories.items():
            found_in_category = []
            for skill in skills:
                if skill.lower() in lower_text:
                    found_in_category.append(skill)
            if found_in_category:
                if category not in found:
                    found[category] = set()
                found[category].update(found_in_category)

    # Convert sets to sorted lists
    return {cat: sorted(list(skills)) for cat, skills in found.items()}
