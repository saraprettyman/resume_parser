"""Regex patterns and section keywords for resume parsing."""

# --------------------------
# Contact patterns (tight global coverage)
# --------------------------
NAME_PATTERN = (
    r"^(?!.*@)(?!.*\d)"                                     # no emails or digits
    r"((?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+|[A-Z]{2,})"              # first name: titlecase or ALL CAPS
    r"(?:\s+(?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+|[A-Z]{2,}"          # next: titlecase or ALL CAPS
    r"|(?:[a-z]{1,3}(?=\s+[A-ZÀ-Ý])))"                      # lowercase particles
    r"){1,4})"
)

EMAIL_PATTERN = (
    r"[A-Za-z0-9._%+\-]+@"                     # local part
    r"(?:[A-Za-z0-9\-]+\.)+"                   # domain labels
    r"[A-Za-z]{2,24}"                          # TLD
)

PHONE_PATTERN = (
    r"(?:\+?\d{1,3}[\s.\-]?)?"                 # country code
    r"(?:\(?\d{1,4}\)?[\s.\-]?)?"              # optional area code
    r"\d{2,4}[\s.\-]?\d{2,4}[\s.\-]?\d{2,6}"   # main number
    r"(?:\s*(?:ext\.?|x)\s*\d{1,5})?"          # extension
)

LINKEDIN_PATTERN = (
    r"(?:https?://)?(?:[a-z]{2,3}\.)?"
    r"linkedin\.com/(?:in|pub)/[A-Za-z0-9_.\-]+/?(?:\?[^\s]*)?"
)

GITHUB_PATTERN = (
    r"(?:https?://)?(?:www\.)?"
    r"github\.com/[A-Za-z0-9._\-]+/?"
)

URL_PATTERN = (
    r"(?:https?://|www\.)[^\s)<>\]]+[^\s)<>\],.;!?]"
)

# --------------------------
# Education patterns
# --------------------------
EDU_START = [
    r"\beducation\b",
    r"academic\s+(background|history)",
    r"training\s+and\s+education",
]
EDU_END = [
    r"\bexperience\b",
    r"work\s+history",
    r"skills",
    r"certifications?",
    r"projects?",
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
GPA_PATTERN = (
    r"(?:GPA|G\.P\.A)\s*[:\s]?\s*([0-4](?:[.,]\d{1,2})?)"
    r"(?:\s*/\s*([0-4](?:[.,]\d{1,2})?))?"
)
DEGREE_KEYWORD_PATTERN = (
    r"\b(?:Bachelor(?:'s)?|Master(?:'s)?|Associate(?:'s)?|Doctor(?:ate)?|"
    r"B\.S\.|BSc|BS|M\.S\.|MS|Ph\.D\.|PhD)\b"
)
PROJECTS_PATTERN = (
    r"(?:Relevant Projects?|Projects?)\s*[:\-–]?"
    r"\s*((?:.*?)(?=(?:\n\s*\n|$)))"
)
MINORS_PATTERN = r"Minors?\s*[:\-–]?\s*([^\n|]+)"
SCHOLARSHIPS_PATTERN = (
    r"(?:Scholarships?|Awards?)\s*[:\-–]?"
    r"\s*((?:.*?)(?=(?:\n\s*\n|$)))"
)
LOCATION_PATTERN = (
    r"\b("
    r"(?:[A-Za-z][A-Za-z .'\-]+,\s*(?:[A-Z]{2}|[A-Za-z][A-Za-z .'\-]+))"
    r"|(?:Remote|Hybrid|On[- ]?site|WFH|Work\s*From\s*Home)"
    r")\s*$"
)
DEGREE_TERM_BLOCKLIST = {
    "science", "sciences", "mathematics", "statistics",
    "computer", "computers", "applied", "engineering",
    "arts", "business", "information", "systems",
    "system", "technology", "technologies",
    "intelligence", "analytics",
    "electrical", "mechanical", "civil",
    "physics", "chemistry", "biology", "biological",
    "computational",
}

# --------------------------
# Experience patterns
# --------------------------
EXP_START = [
    r"professional\s+experience",
    r"experience",
    r"work\s+history",
    r"employment(?:\s+history)?",
]

EXP_END = [
    r"education",
    r"skills",
    r"certifications",
    r"projects",
    r"additional\s+information",
]
MONTH_NAMES_PATTERN = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
DATE_TOKEN_PATTERN = (
    rf"(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|\d{{4}})"
)
DATE_RANGE_PATTERN = (
    rf"({DATE_TOKEN_PATTERN})\s*(?:-|–|to|—)\s*"
    rf"(Present|present|{DATE_TOKEN_PATTERN})"
)
EXPERIENCE_LOCATION_PATTERN = (
    r"^(?:[A-Za-z][A-Za-z .'\-]+,\s*(?:[A-Z]{2}|\d{4,5}|[A-Za-z][A-Za-z .'\-]+))$"
    r"|^(?:Remote|Hybrid|On[- ]?site|WFH|Work\s*From\s*Home)$"
)
EXPERIENCE_ENTRY_PATTERN = rf"""
^
(?P<title>[^\n]+?)\s+
(?P<start>{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*[-–]\s*
(?P<end>(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present))\s*\n
(?P<company>[A-Za-z0-9&.,\- ]{{3,}})
(?:\s+(?P<location>[A-Za-z0-9&.,\- ]{{2,}}))?
(?:\n
    (?P<details>
        (?:
            (?!^(
                [^\n]+?\s+(?:{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*[-–]\s*(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present)
                |
                (?:{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*[-–]\s*(?:{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present)
            ))
            .*
            (?:\n|$)
        )*
    )
)?
"""

# Pipe-delimited experience patterns
EXPERIENCE_PIPE_PATTERN_4 = rf"""
^
(?P<title>[^|\n]+?)\s*\|\s*
(?P<company>[^|\n]+?)\s*\|\s*
(?P<location>[^|\n]+?)\s*\|\s*
(?P<start>{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*(?:–|-|to)\s*
(?P<end>{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present)
(?:\n(?P<details>(?:.+\n?)*))?
"""

EXPERIENCE_PIPE_PATTERN_3 = rf"""
^
(?P<title>[^|\n]+?)\s*\|\s*
(?P<company>[^|\n]+?)\s*\|\s*
(?P<start>{MONTH_NAMES_PATTERN}\s+\d{{4}})\s*(?:–|-|to)\s*
(?P<end>{MONTH_NAMES_PATTERN}\s+\d{{4}}|Present)
(?:\n(?P<details>(?:.+\n?)*))?
"""

# --------------------------
# Summary patterns
# --------------------------
SUMMARY_START = [
    r"professional\s+summary",
    r"summary",
    r"profile",
    r"objective",
]
SUMMARY_END = [
    r"experience",
    r"work\s+history",
    r"skills",
    r"education",
]
