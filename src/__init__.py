"""
Digital Resume Solutions LLC - Resume Parser Package
This package parses PDF and DOCX resumes to extract and count known skills.
"""

from .parser import parse_resume

__all__ = ["parse_resume"]
