# config/patterns.py
# Common regex patterns and section keywords
import re

# --------------------------
# Contact patterns
# --------------------------
NAME_PATTERN = r"^(?!.*@)(?!.*\d)([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})$"
EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_PATTERN = r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}"
LINKEDIN_PATTERN = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+"
GITHUB_PATTERN = r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+"
URL_PATTERN = r"(?:https?://|www\.)[^\s)<]+"

# --------------------------
# Education patterns
# --------------------------
EDU_START = [
    r"\beducation\b",
    r"academic\s+(background|history)",
    r"training\s+and\s+education"
]
EDU_END = [
    r"\bexperience\b",
    r"work\s+history",
    r"skills",
    r"certifications?",
    r"projects?"
]
DATE_RANGE = (
    r"(?:"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{4}\s*[-–]\s*(?:"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{4}|Present|(?:19|20)\d{2})"
    r"|(?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|Present)"
    r"|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{4}"
    r"|(?:19|20)\d{2}"
    r"|Present"
    r")"
)
GPA_PATTERN = r"(?:GPA|G\.P\.A)\s*[:\s]?\s*([0-4](?:[.,]\d{1,2})?)(?:\s*/\s*([0-4](?:[.,]\d{1,2})?))?"
DEGREE_KEYWORD_PATTERN = r"\b(?:Bachelor(?:'s)?|Master(?:'s)?|Associate(?:'s)?|Doctor(?:ate)?|B\.S\.|BSc|BS|M\.S\.|MS|Ph\.D\.|PhD)\b"
PROJECTS_PATTERN = r"(?:Relevant Projects?|Projects?)\s*[:\-–]?\s*((?:.*?)(?=(?:\n\s*\n|$)))"
MINORS_PATTERN = r"Minors?\s*[:\-–]?\s*([^\n|]+)"
SCHOLARSHIPS_PATTERN = r"(?:Scholarships?|Awards?)\s*[:\-–]?\s*((?:.*?)(?=(?:\n\s*\n|$)))"
LOCATION_PATTERN = (
    r"\b("
    r"(?:[A-Za-z][A-Za-z .'\-]+,\s*(?:[A-Z]{2}|[A-Za-z][A-Za-z .'\-]+))"
    r"|(?:Remote|Hybrid|On[- ]?site|WFH|Work\s*From\s*Home)"
    r")\s*$"
)
DEGREE_TERM_BLOCKLIST = {
    "science", "mathematics", "statistics", "computer", "data", "applied",
    "engineering", "arts", "business", "information", "systems",
    "intelligence", "analytics",
}

# --------------------------
# Experience patterns
# --------------------------
EXP_START = [
    r"experience",
    r"work\s+history",
    r"employment(?:\s+history)?"
]
EXP_END = [
    r"education",
    r"skills",
    r"certifications",
    r"projects"
]
MONTH_NAMES_PATTERN = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
DATE_TOKEN_PATTERN = rf"(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|\d{{4}})"
DATE_RANGE_PATTERN = rf"({DATE_TOKEN_PATTERN})\s*(?:-|–|to|—)\s*(Present|present|{DATE_TOKEN_PATTERN})"
EXPERIENCE_LOCATION_PATTERN = (
    r"^(?:[A-Za-z][A-Za-z .'\-]+,\s*(?:[A-Z]{2}|\d{{4,5}}|[A-Za-z][A-Za-z .'\-]+))$"
    r"|^(?:Remote|Hybrid|On[- ]?site|WFH|Work\s*From\s*Home)$"
)
EXPERIENCE_ENTRY_PATTERN = rf"""
^
(?P<title>[^\n]+?)\s+
(?P<start>{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*[-–]\s*
(?P<end>(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present))\s*\n
(?P<company>[^\n]+)
(?:\s+(?P<location>[^\n]+))?
(?:\n(?P<details>(?:(?!^([^\n]+?\s+(?:{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*[-–]\s*(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present)|(?:{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*[-–]\s*(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present))).*(?:\n|$))*))?
"""

# --------------------------
# Summary patterns
# --------------------------
SUMMARY_START = [r"professional\s+summary", r"summary", r"profile", r"objective"]
SUMMARY_END = [r"experience", r"work\s+history", r"skills", r"education"]
