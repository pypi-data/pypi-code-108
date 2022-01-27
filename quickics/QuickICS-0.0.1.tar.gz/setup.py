from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / 'README.md', 'r') as f:
    long_description = f.read()

setup(
    name="QuickICS",
    version="0.0.1",
    author="M. Holbert Roberts",
    author_email="mhr320@gmail.com",
    description="quick way to convert a csv file of events for same type event to .ics file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhr320/QuickICS",
    package_dir={'here': 'quickics'},
    packages=find_packages(),
    package_data={},
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.8, <4'
    )
