"""
text_normalizer.py

Provides utilities for normalizing text whitespace and line breaks.

The primary function in this module ensures that text is cleaned of inconsistent
spacing, excess blank lines, and platform-specific newline styles. This is
especially useful when processing resumes or other structured documents where
consistent formatting is critical for parsing.

Functions:
    normalize_whitespace(text: str) -> str:
        Cleans and standardizes whitespace in the input text.
"""
def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace and line breaks in the given text.

    Steps performed:
    1. Converts all Windows (`\r\n`) and old Mac (`\r`) line endings to Unix-style (`\n`).
    2. Strips trailing spaces from each line.
    3. Removes leading and trailing empty lines.
    4. Collapses multiple consecutive blank lines into a single blank line.
    5. Preserves intentional single blank lines for readability.
    6. Strips leading/trailing whitespace from the final text.

    Args:
        text (str): The input text to normalize. If None, returns an empty string.

    Returns:
        str: The whitespace-normalized text.
    """
    if text is None:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces from each line
    lines = [ln.rstrip() for ln in text.split("\n")]

    # Strip leading empty lines
    while lines and not lines[0].strip():
        lines.pop(0)

    # Strip trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    # Collapse multiple blank lines into one
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

    # Return cleaned text
    return "\n".join(normalized).strip()
