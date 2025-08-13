import pytest
from pathlib import Path

@pytest.fixture(params=Path("tests/data/fake_resumes").glob("*.txt"))
def fake_resume_path(request):
    """Yields each fake resume path for parameterized testing."""
    return request.param
