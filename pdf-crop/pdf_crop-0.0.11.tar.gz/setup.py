from pathlib import Path
from setuptools import setup, find_packages
import io
import os


VERSION = "0.0.11"


def read(*paths, **kwargs):
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pdf_crop",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=VERSION,
    description="A commandline tool to crop a PDF into sub-PDFs",
    classifiers=[],
    keywords="PDF, Crop",
    author="wniu99",
    author_email="niuwei95@gmail.com",
    url="https://www.niuwei.info",
    license="FreeBSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["pymupdf", "imageio", "rich", "numpy"],
    entry_points={"console_scripts": ["pdf_crop = pdf_crop.__main__:main"]},
)
