"""
Pytest fixtures for loading test resume files.

This module provides parameterized fixtures to supply fake resume file
paths to tests. The fixtures iterate over the `tests/data/fake_resumes`
directory and return one file path per test run.
"""

from pathlib import Path
import pytest

@pytest.fixture(params=(Path(__file__).parent / "data" / "fake_resumes").glob("*.pdf"))
def fake_resume_path(request):
    """
    Yields each fake resume path for parameterized testing.

    This will automatically parameterize tests with all .txt files in
    tests/data/fake_resumes, so each test run gets one resume path.
    """
    return request.param
