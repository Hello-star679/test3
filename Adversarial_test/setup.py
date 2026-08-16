#!/usr/bin/env python
"""
Setup script for the adversarial test framework.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="adversarial-content-test",
    version="1.0.0",
    author="Internal Security Team",
    description="GAN-style adversarial testing framework for content classifiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/adversarial-content-test",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "local": ["transformers>=4.35.0", "torch>=2.1.0"],
        "openai": ["openai>=0.28.0"],
        "monitoring": ["psutil>=5.9.6"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "adversarial-test=scripts.run_test:main",
            "analyze-results=scripts.analyze_results:main",
            "diagnose-classifier=scripts.diagnose_classifier:main",
        ],
    },
)
