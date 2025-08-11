# utils/section_finder.py
import re
from typing import List

def find_section(text: str, start_keywords: List[str], end_keywords: List[str]) -> str:
    if not text:
        return ""
    start_pattern = r"(?mi)^\s*(?P<header>(" + "|".join(start_keywords) + r"))\s*[:\-–—]?\s*$"
    # find all header lines
    headers = list(re.finditer(start_pattern, text))
    if not headers:
        # fallback: try searching inline
        inline_pat = r"(?si)(" + "|".join(start_keywords) + r")\s*[:\-–—]?\s*(.*?)(?=(?:\n[A-Z][^\n]*\n)|$)"
        m = re.search(inline_pat, text)
        if m:
            return m.group(2).strip()
        return ""
    # take first header occurrence
    first = headers[0]
    start_idx = first.end()
    # find next section header from end_keywords
    end_pattern = r"(?mi)^\s*(?P<header>(" + "|".join(end_keywords) + r"))\s*[:\-–—]?\s*$"
    next_hdr = re.search(end_pattern, text[start_idx:], re.MULTILINE | re.IGNORECASE)
    if next_hdr:
        end_idx = next_hdr.start() + start_idx
    else:
        end_idx = len(text)
    return text[start_idx:end_idx].strip()
