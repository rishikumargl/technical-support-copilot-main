"""
Setup configuration for ingestion_pipeline package.

Install with: pip install -e .
"""

from setuptools import setup, find_packages

with open("config/requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip()]

with open("docs/README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ingestion-pipeline",
    version="1.0.0",
    author="Technical Support Copilot Team",
    description="Enterprise RAG Document Ingestion Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/technical-support-copilot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    package_data={
        "ingestion_pipeline": [
            "config/requirements.txt",
            "docs/*.md",
            "docs/*.txt",
            "data/**/*",
            "output/**/*",
        ],
    },
)
