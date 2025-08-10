import os
from src.utils.file_reader import read_resume
from src.utils.extractor import (
    extract_role_skills,
    extract_all_technical_skills,
    extract_certifications
)
from src.utils.skills_loader import load_skills

def main():
    print("====================================")
    print("   📄 Resume Skill Analyzer CLI")
    print("====================================\n")

    # Step 1: Ask for resume path
    resume_path = input("Enter path to resume file: ").strip()
    if not os.path.exists(resume_path):
        print("[ERROR] File not found. Exiting.")
        return

    resume_text = read_resume(resume_path)

    # Step 2: Load skills.json
    skills_dict = load_skills()

    # Step 3: Choose mode
    print("\nChoose review mode:")
    print("1. General Review (all technical skills + certifications)")
    print("2. Specific Role Review (role-based skills + certifications)")
    mode_choice = input("Enter choice [1 or 2]: ").strip()

    if mode_choice == "1":
        found_skills = extract_all_technical_skills(resume_text, skills_dict)
        found_certs = extract_certifications(resume_text, skills_dict)

        print("\n📊 General Technical Skills Found:")
        if found_skills:
            print("  " + ", ".join(found_skills))
        else:
            print("  None")

        print("\n🎓 Certifications Found:")
        if found_certs:
            print("  " + ", ".join(found_certs))
        else:
            print("  None")

    elif mode_choice == "2":
        roles_dict = skills_dict.get("ROLES", {})
        roles = list(roles_dict.keys())

        if not roles:
            print("[ERROR] No roles found in skills file.")
            return

        print("\nAvailable roles:")
        for idx, role in enumerate(roles, start=1):
            print(f"  {idx}. {role}")

        role_choice = input("\nEnter role number: ").strip()
        if not role_choice.isdigit() or not (1 <= int(role_choice) <= len(roles)):
            print("[ERROR] Invalid choice. Exiting.")
            return

        selected_role = roles[int(role_choice) - 1]

        found_skills = extract_role_skills(resume_text, skills_dict, selected_role)
        found_certs = extract_certifications(resume_text, skills_dict, role=selected_role)

        print(f"\n📊 Skills Found for {selected_role}:")
        if found_skills:
            print("  " + ", ".join(found_skills))
        else:
            print("  None")

        print(f"\n🎓 Certifications Found for {selected_role}:")
        if found_certs:
            print("  " + ", ".join(found_certs))
        else:
            print("  None")

    else:
        print("[ERROR] Invalid mode selected.")

if __name__ == "__main__":
    main()
