"""
Setup configuration for TrackMaster package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="trackmaster",
    version="1.3.1",
    author="TrackMaster Team",
    author_email="info@trackmaster.com",
    description="AI-powered audio mastering server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kerze-Mann/TrackMaster",
    project_urls={
        "Bug Tracker": "https://github.com/Kerze-Mann/TrackMaster/issues",
        "Documentation": "https://github.com/Kerze-Mann/TrackMaster#readme",
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
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trackmaster=trackmaster.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
