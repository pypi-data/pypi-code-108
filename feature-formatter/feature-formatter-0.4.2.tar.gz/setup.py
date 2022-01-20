#!/usr/bin/env python3
"""atext-formatter setup"""

from distutils.core import setup

from setuptools import find_packages

setup(
    name="feature-formatter",
    version="0.4.2",
    description="A smart formatter to translate raw text into readable text",
    author="Bob Zhou",
    author_email="bob.zhou@ef.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="text audio formatter",
    url="",
    packages=find_packages(exclude=["contrib", "docs", "tests*", "venv"]),
    install_requires=["num2words", "numpy"],
    tests_require=["pytest", "pytest-cov", "pytest-mock", "coverage"],
    python_requires=">=3.5, <4",
    entry_points={"console_scripts": []},
)
