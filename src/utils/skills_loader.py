import json
import os

def load_skills(file_path=None):
    """Load the full skills dictionary from JSON file."""
    if file_path is None:
        # Always resolve relative to project root
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "..", "data", "skills_master.json")
        file_path = os.path.abspath(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
