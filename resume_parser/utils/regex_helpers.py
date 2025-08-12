# utils/regex_helpers.py
import re
from typing import List, Optional

def find_first(pattern: str, text: str, flags=re.IGNORECASE) -> Optional[str]:
    match = re.search(pattern, text, flags)
    return match.group(0).strip() if match else None

def find_all(patterns: List[str], text: str, flags=re.IGNORECASE):
    matches = []
    for p in patterns:
        matches.extend(re.findall(p, text, flags))
    return matches

def safe_search(pattern: str, text: str, flags=re.IGNORECASE):
    return bool(re.search(pattern, text, flags))
