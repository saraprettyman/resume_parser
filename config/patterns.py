# config/patterns.py
# Common regex patterns and section keywords
import re

# Degree recognition
DEGREE_PATTERNS = [
    r"bachelor(?:'s)?\s+of\s+[A-Za-z &]+",
    r"master(?:'s)?\s+of\s+[A-Za-z &]+",
    r"associate(?:'s)?\s+degree(?:\s+in)?\s+[A-Za-z &]+",
    r"ph\.?d\.?|doctorate(?:\s+in)?\s+[A-Za-z &]+",
    r"high\s+school\s+diploma",
    r"\bGED\b",
    r"\bcertificate\b"
]

# GPA pattern capturing 3.73 or 3.73/4.0 formats
GPA_PATTERN = r"(?:GPA|G\.P\.A)\s*[:\s]?\s*([0-4](?:[.,]\d{1,2})?)(?:\s*/\s*([0-4](?:[.,]\d{1,2})?))?"

# Months & dates
MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
MONTH_YEAR = rf"{MONTHS}\s+\d{{4}}"
YEAR = r"\b(19|20)\d{2}\b"
DATE_RANGE = rf"(?:{MONTH_YEAR}\s*[-–]\s*(?:{MONTH_YEAR}|Present|{YEAR})|{YEAR}\s*[-–]\s*(?:{YEAR}|Present)|{MONTH_YEAR}|{YEAR}|Present)"

# Section keywords
SUMMARY_START = [r"professional\s+summary", r"summary", r"profile", r"objective"]
SUMMARY_END = [r"experience", r"work\s+history", r"skills", r"education"]

EDU_START = [r"\beducation\b", r"academic\s+(background|history)", r"training\s+and\s+education"]
EDU_END = [r"\bexperience\b", r"work\s+history", r"skills", r"certifications?", r"projects?"]

EXP_START = [r"experience", r"work\s+history", r"employment(?:\s+history)?"]
EXP_END = [r"education", r"skills", r"certifications", r"projects"]

SKILLS_START = [r"skills", r"technical\s+skills", r"technical\s+proficiencies", r"competencies"]
SKILLS_END = [r"experience", r"education", r"certifications", r"projects"]

CERT_START = [r"certifications?", r"licenses?", r"credentials?"]
CERT_END = [r"experience", r"education", r"skills", r"projects"]

# Contact patterns
NAME_PATTERN = r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}"
EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_PATTERN = r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}"
LINKEDIN_PATTERN = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+"
GITHUB_PATTERN = r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+"
URL_PATTERN = r"(?:https?://|www\.)[^\s<]+"


EDU_PATTERN = re.compile(
    r"""
    (?P<institution>[A-Z][A-Za-z&.,'\s]+(?:University|College|Institute|School))  # Institution
    (?:\s*\|\s*(?P<location>[A-Za-z\s]+,\s*[A-Za-z]{2,}))?                        # Optional location: City, State
    \s+
    (?P<grad_date>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|
                   May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|
                   Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)?\s?\d{4})            # Grad date
    [\s\S]{0,50}?                                                                 # Short gap
    (?P<degree>(?:Bachelor|Master|Associate|Doctor)[^:\n]*)                       # Degree
    (?::\s*(?P<emphasis>[^\n]*))?                                                 # Optional emphasis
    (?:.*?GPA[:\s]*(?P<gpa>\d\.\d{1,2})\s*/\s*4\.0+)?                             # Optional GPA anywhere
    """,
    re.VERBOSE | re.IGNORECASE
)
