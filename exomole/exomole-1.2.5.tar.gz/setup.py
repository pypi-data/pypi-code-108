from setuptools import setup, find_packages
from pathlib import Path

root = Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (root / "README.rst").read_text(encoding="utf-8")

setup(
    name="exomole",
    version="1.2.5",
    description="A package for parsing and validation of Exomol Database data files",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/hanicinecm/exomole/",
    author="Martin Hanicinec",
    author_email="hanicinecm@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ],
    keywords="exomol",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["pandas", "requests", "pyvalem>=2.3"],
    extras_require={
        "dev": ["pytest-cov", "tox", "black", "ipython"],
    },
    project_urls={
        "Bug Reports": "https://github.com/hanicinecm/exomole/issues",
    },
)
