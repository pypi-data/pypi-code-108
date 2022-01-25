import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name = "inspec-ai",
    version = "0.1.5",
    license="Internal Use", # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="Library containing all the prototypes that were developped by the Moov AI product team.",
    long_description=README,
    long_description_content_type="text/markdown",
    url = "https://moov.ai/en/",
    author = "MoovAI Technologies Inc",
    author_email = "info@moov.ai",
    classifiers=[
        "Development Status :: 3 - Alpha", # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    packages = find_packages(),
    include_package_data=True,
    install_requires=[
        "fuzzywuzzy>=0.18",
        "numpy>=1",
        "pandas>=1",
        "pandas-profiling>=3",
        "scikit-learn>=1"
    ],
    entry_points={},
)