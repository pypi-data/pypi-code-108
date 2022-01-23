import os
import setuptools

from datetime import datetime
from distutils.core import setup

# Read the contents of README.md
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Identify version number
def get_version() -> str:
    parent_dir = os.path.dirname(__file__)
    version_file = os.path.join(parent_dir, "VERSION.txt")
    assert os.path.isfile(version_file)
    with open(version_file) as fh:
        version = fh.read().strip()

    version_parts = version[1:].split(".")
    valid_version = (
        len(version) >= 5
        and version[0] == "v"
        and len(version_parts) >= 3
        and version_parts[0].isdigit()
        and version_parts[1].isdigit()
        and version_parts[2].isdigit()
    )
    assert valid_version

    return version.strip("v")


version = get_version()

setup(
    name="flyr",
    packages=["flyr", "flyr.palettes"],
    version=version,
    license="EUPL v1.2",
    description="Flyr is a library for extracting thermal data from FLIR images written fully in Python, without depending on ExifTool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Arthur Nieuwland",
    author_email="anieuwland@nimmerfort.eu",
    url="https://bitbucket.org/nimmerwoner/flyr/",
    project_urls={
        "Issues": "https://bitbucket.org/nimmerwoner/flyr/issues?status=new&status=open",
        "Releases": "https://bitbucket.org/nimmerwoner/flyr/downloads/",
        "Author website": "http://nimmerfort.eu",
    },
    download_url=f"https://bitbucket.org/nimmerwoner/flyr/downloads/flyr-{version}.tar.gz",
    keywords=["flir", "thermography", "heat imagery"],
    install_requires=["numpy", "nptyping==0.3.1", "pillow"],
    python_requires=">=3.5",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    entry_points={"console_scripts": ["flyr=flyr.flyr:main"]},
)
