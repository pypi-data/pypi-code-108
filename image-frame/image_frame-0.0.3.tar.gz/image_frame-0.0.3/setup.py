# read the contents of your README file
from pathlib import Path

from setuptools import setup

readme_path = Path(r"Z:\dev\image_frame\readme.md")
long_description = readme_path.read_text()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
)
