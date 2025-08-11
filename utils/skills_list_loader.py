# utils/skills_list_loader.py
import json
import os

def load_skills(file_path=None):
    if file_path is None:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join("data", "skills_master.json")
        file_path = os.path.abspath(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_roles(file_path=None):
    skills = load_skills(file_path)
    return list(skills.get("ROLES", {}).keys())
