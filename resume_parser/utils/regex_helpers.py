# utils/regex_helpers.py
import re
from typing import List, Optional
from config.patterns import URL_PATTERN

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

def find_additional_urls(text: str, known_urls: List[str], flags=re.IGNORECASE) -> List[str]:
    """
    Return all URLs in `text` excluding those in `known_urls`.
    Comparison is case-insensitive and ignores trailing slashes.
    """
    urls = re.findall(URL_PATTERN, text, flags)
    cleaned_known = {ku.rstrip('/').lower() for ku in known_urls if ku}
    return [
        u.rstrip('/')
        for u in urls
        if u.rstrip('/').lower() not in cleaned_known
    ]
