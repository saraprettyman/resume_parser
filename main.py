import json
import csv
from pathlib import Path
from src.utils.extractor import ResumeSkillExtractor
from src.utils.file_reader import read_resume

# ANSI color codes
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"

def divider():
    print(f"{YELLOW}{'-' * 60}{RESET}")

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved JSON to {filename}")

def save_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if "present" in data and "missing" in data:
            writer.writerow(["Category", "Status", "Skills"])
            for cat, skills in data["present"].items():
                writer.writerow([cat, "Present", ", ".join(skills)])
            for cat, skills in data["missing"].items():
                writer.writerow([cat, "Missing", ", ".join(skills)])
        else:
            writer.writerow(["Category", "Skills"])
            for category, skills in data.items():
                writer.writerow([category, ", ".join(skills)])
    print(f"[+] Saved CSV to {filename}")

def save_markdown(data, filename, role_name=None):
    with open(filename, "w", encoding="utf-8") as f:
        if "present" in data and "missing" in data:
            f.write(f"# Role-Specific Skills Report: {role_name or ''}\n\n")
            f.write("## Present Skills\n")
            for cat, skills in data["present"].items():
                f.write(f"### {cat}\n")
                f.write("\n".join(f"- {skill}" for skill in skills) if skills else "_None_")
                f.write("\n\n")
            f.write("## Missing Skills\n")
            for cat, skills in data["missing"].items():
                f.write(f"### {cat}\n")
                f.write("\n".join(f"- {skill}" for skill in skills) if skills else "_None_")
                f.write("\n\n")
        else:
            f.write("# Skills Extraction Report\n\n")
            for category, skills in data.items():
                f.write(f"## {category}\n")
                f.write("\n".join(f"- {skill}" for skill in skills) if skills else "_None_")
                f.write("\n\n")
    print(f"[+] Saved Markdown to {filename}")

def choose_output(data, role_name=None):
    save_choice = input("Do you want to save the results? (y/n): ").strip().lower()
    if save_choice == "y":
        fmt = input("Choose output format (json/csv/md): ").strip().lower()
        filename = input("Enter output file name (with extension): ").strip()
        if fmt == "json":
            save_json(data, filename)
        elif fmt == "csv":
            save_csv(data, filename)
        elif fmt == "md":
            save_markdown(data, filename, role_name)
        else:
            print("[!] Invalid format. Skipping save.")

def load_roles():
    try:
        skills_file = Path(__file__).resolve().parent / "src" / "data" / "skills_master.json"
        with open(skills_file, "r", encoding="utf-8") as f:
            skills_data = json.load(f)
        return list(skills_data.get("roles", {}).keys())
    except Exception as e:
        print(f"[ERROR] Could not load roles: {e}")
        return []

def interactive_cli():
    print(f"{BOLD}{CYAN}=== Resume Skills Extraction Tool ==={RESET}")
    resume_path = input("Enter path to resume file: ").strip()
    extractor = ResumeSkillExtractor()

    print("\n[INFO] Reading resume...")
    try:
        resume_text = read_resume(resume_path)
    except Exception as e:
        print(f"[ERROR] Failed to read resume: {e}")
        return

    print("\nChoose analysis mode:")
    print("1. General Skills Review")
    print("2. Role-Specific Skills Review")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        results = extractor.extract_general_skills(resume_text)
        divider()
        print(f"{BOLD}{CYAN}GENERAL SKILLS REVIEW{RESET}")
        divider()
        for category, skills in results.items():
            color = GREEN if skills else RED
            skill_list = "\n  - ".join(skills) if skills else "None"
            print(f"{BOLD}{CYAN}{category}:{RESET} {color}")
            print(f"  - {skill_list}{RESET}")
            print()
        divider()
        choose_output(results)

    elif choice == "2":
        roles = load_roles()
        if not roles:
            print("[ERROR] No roles found in skills_master.json")
            return

        print("\nAvailable roles:")
        for i, role in enumerate(roles, start=1):
            print(f"{i}. {role}")

        role_choice = input("Select role by number: ").strip()
        try:
            role_name = roles[int(role_choice) - 1]
        except (IndexError, ValueError):
            print("[!] Invalid selection.")
            return

        results = extractor.extract_role_specific(resume_text, role_name)
        divider()
        print(f"{BOLD}{CYAN}ROLE-SPECIFIC REVIEW: {role_name}{RESET}")
        divider()

        print(f"\n{BOLD}{GREEN}PRESENT SKILLS:{RESET}")
        for category, skills in results["present"].items():
            skill_list = "\n  - ".join(skills) if skills else "None"
            print(f"{BOLD}{CYAN}{category}:{RESET} {GREEN}")
            print(f"  - {skill_list}{RESET}")
            print()

        print(f"{BOLD}{RED}MISSING SKILLS:{RESET}")
        for category, skills in results["missing"].items():
            skill_list = "\n  - ".join(skills) if skills else "None"
            print(f"{BOLD}{CYAN}{category}:{RESET} {RED}")
            print(f"  - {skill_list}{RESET}")
            print()

        divider()
        choose_output(results, role_name)
    else:
        print("[!] Invalid choice.")

if __name__ == "__main__":
    interactive_cli()
