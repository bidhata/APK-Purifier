#!/usr/bin/env python3
"""
Setup script for APK Purifier
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="apk-purifier",
    version="1.0.0",
    description="A cross-platform desktop application for purifying Android APK files by removing advertisements and basic malware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Krishnendu Paul",
    author_email="me@krishnendu.com",
    url="https://github.com/bidhata/APK-Purifier",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": ["data/*.txt", "resources/*"],
    },
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "apk-purifier=main:main",
            "apk-purifier-cli=cli:main",
        ],
        "gui_scripts": [
            "apk-purifier-gui=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
        "Topic :: Utilities",
        "Environment :: X11 Applications :: Qt",
    ],
    keywords="android apk purifier ads malware removal signing",
    project_urls={
        "Bug Reports": "https://github.com/bidhata/APK-Purifier/issues",
        "Source": "https://github.com/bidhata/APK-Purifier",
        "Documentation": "https://github.com/bidhata/APK-Purifier/wiki",
        "Author Website": "https://krishnendu.com",
    },
)