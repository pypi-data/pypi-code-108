"""Instructions for installing the app"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'ntbk',
    version = '0.2.0',
    author = 'Blake Bengtson',
    author_email = 'blake@bengtson.us',
    license = 'MIT',
    description = 'A simple, opinionated terminal notebook inspired by bullet journaling.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/bbeng89/ntbk',
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities"
    ],
    entry_points = {
        'console_scripts': [
            'ntbk=ntbk.main:run'
        ]
    }
)
