import os
import json
from src.utils.file_reader import read_pdf, read_docx
from src.utils.extractor import extract_skills, extract_all_technical_skills

# ====== CONFIG ======
file_path = "tests/sample_resume.pdf"  # Change to your file
mode = "all"  # "role" or "all"
role = "Data Engineering"  # Only used if mode = "role"
skills_file = "data/skills_master.json"
# =====================

# Load skills master JSON
with open(skills_file, "r", encoding="utf-8") as f:
    skills_master = json.load(f)

# Detect file type and read text
ext = os.path.splitext(file_path)[1].lower()
if ext == ".pdf":
    resume_text = read_pdf(file_path)
elif ext == ".docx":
    resume_text = read_docx(file_path)
else:
    raise ValueError(f"Unsupported file type: {ext}")

# Extract skills based on mode
if mode == "role":
    if role not in skills_master:
        raise ValueError(f"Role '{role}' not found in skills_master")
    relevant_skills = extract_skills(resume_text, role, skills_master)
    print(f"Skills for role '{role}':")
    print(json.dumps(relevant_skills, indent=2))
elif mode == "all":
    all_skills = extract_all_technical_skills(resume_text, skills_master)
    print("All technical skills found:")
    print(json.dumps(all_skills, indent=2))
else:
    raise ValueError("Invalid mode. Use 'role' or 'all'.")
