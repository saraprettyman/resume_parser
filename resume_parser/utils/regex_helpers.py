"""
regex_helpers.py

Utility functions for performing common regex search and extraction tasks.
Includes helpers for finding the first match, all matches, safe boolean checks,
and filtering URLs.
"""

import re
from typing import List, Optional
from resume_parser.config.patterns import URL_PATTERN


def find_first(pattern: str, text: str, flags: int = re.IGNORECASE) -> Optional[str]:
    """
    Finds the first match of a regex pattern in the given text.

    Args:
        pattern: Regex pattern string.
        text: Text to search within.
        flags: Optional regex flags (default: re.IGNORECASE).

    Returns:
        The matched string with leading/trailing spaces removed, or None if no match is found.
    """
    match = re.search(pattern, text, flags)
    return match.group(0).strip() if match else None


def find_all(patterns: List[str], text: str, flags: int = re.IGNORECASE) -> List[str]:
    """
    Finds all matches for multiple regex patterns in the given text.

    Args:
        patterns: A list of regex pattern strings.
        text: Text to search within.
        flags: Optional regex flags (default: re.IGNORECASE).

    Returns:
        A list of all matched strings from all provided patterns.
    """
    matches = []
    for p in patterns:
        matches.extend(re.findall(p, text, flags))
    return matches


def safe_search(pattern: str, text: str, flags: int = re.IGNORECASE) -> bool:
    """
    Checks whether a regex pattern exists in the given text.

    This function returns a boolean without raising errors for missing matches.

    Args:
        pattern: Regex pattern string.
        text: Text to search within.
        flags: Optional regex flags (default: re.IGNORECASE).

    Returns:
        True if the pattern is found, False otherwise.
    """
    return bool(re.search(pattern, text, flags))


def find_additional_urls(
    text: str,
    known_urls: List[str],
    flags: int = re.IGNORECASE
) -> List[str]:
    """
    Finds all unique URLs in `text` that are not in `known_urls`.

    Matching is case-insensitive and ignores trailing slashes in both sources.

    Args:
        text: The text to search within.
        known_urls: List of URLs to exclude from the result.
        flags: Optional regex flags (default: re.IGNORECASE).

    Returns:
        A list of new URLs found in the text, with trailing slashes removed.
    """
    urls = re.findall(URL_PATTERN, text, flags)
    cleaned_known = {ku.rstrip('/').lower() for ku in known_urls if ku}
    return [
        u.rstrip('/')
        for u in urls
        if u.rstrip('/').lower() not in cleaned_known
    ]
