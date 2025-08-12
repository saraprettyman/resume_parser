"""
section_finder.py

Utility for extracting specific sections from text (e.g., resumes, reports)
based on start and end header keywords.
"""

import re
from typing import List


def find_section(text: str, start_keywords: List[str], end_keywords: List[str]) -> str:
    """
    Extracts a section of text that starts with one of the `start_keywords`
    and ends before one of the `end_keywords`.

    Keyword matches are case-insensitive and can be on their own line
    or inline followed by content.

    Args:
        text: The full text to search.
        start_keywords: List of keywords that can mark the start of the section.
        end_keywords: List of keywords that can mark the start of the next section.

    Returns:
        The extracted section text, stripped of leading/trailing whitespace.
        Returns an empty string if no matching section is found.

    Example:
        >>> text = "Experience\\nCompany A\\nDetails...\\nEducation\\nUniversity..."
        >>> find_section(text, ["experience"], ["education"])
        'Company A\\nDetails...'
    """
    if not text:
        return ""

    # Match a section header on its own line
    start_pattern = r"(?mi)^\s*(?P<header>(" + "|".join(start_keywords) + r"))\s*[:\-–—]?\s*$"

    headers = list(re.finditer(start_pattern, text))
    if not headers:
        # Fallback: keyword appears inline, capture until next capitalized line or EOF
        inline_pattern = (
            r"(?si)(" + "|".join(start_keywords) + r")\s*[:\-–—]?\s*"
            r"(.*?)(?=(?:\n[A-Z][^\n]*\n)|$)"
        )
        m = re.search(inline_pattern, text)
        return m.group(2).strip() if m else ""

    # Take the first header occurrence
    first = headers[0]
    start_idx = first.end()

    # Match the next section header for stopping point
    end_pattern = r"(?mi)^\s*(?P<header>(" + "|".join(end_keywords) + r"))\s*[:\-–—]?\s*$"
    next_hdr = re.search(end_pattern, text[start_idx:])

    if next_hdr:
        end_idx = next_hdr.start() + start_idx
    else:
        end_idx = len(text)

    return text[start_idx:end_idx].strip()
