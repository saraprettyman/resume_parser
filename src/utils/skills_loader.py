import json

def load_skills(file_path="skills_master.json"):
    """Load the full skills dictionary from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
