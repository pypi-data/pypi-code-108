from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / 'README.md', 'r') as f:
    long_description = f.read()

setup(
    name="Wmt2Ics",
    version="0.0.23",
    author="M. Holbert Roberts",
    author_email="mhr320@gmail.com",
    description="Converts wmt schedule Views:My Schedule to .ics file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhr320/Wmt2Ics",
    package_dir={'here': 'wmt2ics'},
    packages=find_packages(),
    package_data={'wmt2ics': ['shift_cats.data', 'wmtconfig.json']},
    install_requires=['icalendar', 'pyperclip'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.8, <4'
    )
