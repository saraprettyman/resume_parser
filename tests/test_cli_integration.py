"""Integration tests for the resume_parser CLI commands."""

import subprocess
import sys
from typing import Any


def test_cli_runs_profile_check(fake_resume_path: Any):
    """
    Runs cli.py in 'Profile / Readability Check' mode with a fake resume.
    """
    simulated_input = f"1\n{fake_resume_path}\n"

    result = subprocess.run(
        [sys.executable, "-m", "resume_parser.cli"],  # run as module to fix relative imports
        input=simulated_input.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
        check=False,  # explicitly set to avoid pylint W1510
    )

    assert result.returncode == 0, f"CLI exited with error: {result.stderr.decode()}"

    output_text = result.stdout.decode()

    # CLI output should contain key section headings
    assert "ATS Profile Check" in output_text
    assert "Professional Summary" in output_text
    assert "Education" in output_text
    assert "Work Experience" in output_text
