# utils/text_normalizer.py
import re

def normalize_whitespace(text: str) -> str:
    if text is None:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    # strip leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # collapse multiple blank lines to one
    normalized = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank <= 1:
                normalized.append("")
        else:
            blank = 0
            normalized.append(ln)
    # join and collapse whitespace inside lines
    return "\n".join(normalized).strip()
