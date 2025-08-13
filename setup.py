"""Setup configuration for the resume_parser package."""

from pathlib import Path
from setuptools import setup, find_packages

# Read README.md for the long description if available
this_dir = Path(__file__).parent
readme_path = this_dir / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read install requirements if requirements.txt exists
requirements_path = this_dir / "requirements.txt"
install_requires = (
    requirements_path.read_text(encoding="utf-8").splitlines()
    if requirements_path.exists()
    else []
)

setup(
    name="resume_parser",
    version="0.1.0",
    author="Sara Prettyman",
    author_email="sara@digitalresumesolutions.org",
    description="A tool to parse resumes for ATS checks, skills, and profile insights.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saraprettyman/resume_parser",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.9",
    include_package_data=True,
    license="GNU",
)
