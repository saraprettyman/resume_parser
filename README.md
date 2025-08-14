<h1 align="center">📄 Resume Parser </h1>
<p align="center"><em>See your technical resume exactly how recruiters and ATS tools see it — and get clear, actionable feedback.</em></p>

<div align="center">

[![GPL License](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Medium](https://img.shields.io/badge/-@saraprettyman-03a147?style=flat)](https://medium.com/@saraprettyman)
[![Buy Me a Coffee](https://img.shields.io/badge/-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee&logoColor=white)](https://buymeacoffee.com/saraprettyman)

<img src="tests/data/cli_screenshot_1.png" alt="CLI Screenshot" width="80%">

</div>

<div><br><br></div>

## 💡 Why This Exists
ATS and recruiter software often strip away formatting, bullets, and design elements — leaving a plain-text version of your resume that can look very different from the PDF you submit. **Resume Parser** reveals that hidden view so you can improve based on facts, not guesswork. Runs entirely **offline** — your data never leaves your machine.


This is a project by **Digital Resume Solutions LLC**, created with a privacy-first approach. Everything runs locally on your machine — your data never leaves your computer.


## 🚀 Features
- **ATS text view** – See the raw text an ATS extracts.  
- **Skills check** – Detect missing job-specific keywords & tech skills.  
- **Recruiter preview** – View a clean, parsed version of your resume.  
- **Formatting audit** – Spot lost layout, bullets, or special chars.  
- **Privacy-first** – 100% local processing.


## 🛠 Skills Checker
<div align="center">
  <img src="tests/data/cli_screenshot_2.png" alt="Skills Checker" width="60%">
</div>  

Scan your resume for **general** or **role-specific** skills from a curated dataset.  
See what’s recognized — and what’s missing.

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/saraprettyman/resume_parser.git
cd resume_parser

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .
```

## 🚀 Launch interactive mode
```bash
python -m resume_parser.cli
```

You’ll be guided through:
1. Selecting your resume
2. Choosing analysis modes (ATS, Skills)
3. Viewing results in your terminal

## 🛠  Development
For local development with tests:
```bash
python -m resume_parser.cli
```
We welcome contributions. If you’d like to add a feature or fix a bug, open an issue or submit a pull request.

## 🗺 Roadmap
* Web interface for drag-and-drop uploads
* Side-by-side diff view of original vs parsed text
* Job posting integration for direct keyword comparison
* Chrome extention

## 📜 License
This project is licensed under the GPLv3 License.

Created by Digital Resume Solutions LLC
If you find this useful, [Buy Me a Coffee](https://buymeacoffee.com/saraprettyman) to support continued development.

