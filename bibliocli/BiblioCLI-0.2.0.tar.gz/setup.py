from importlib.metadata import entry_points

from setuptools import setup

setup(
    name="BiblioCLI",
    version="0.2.0",
    description="A command line interface for capturing and storing information about books you want to read",
    url="https://github.com/KeaganStokoe/biblioCLI",
    author="Keagan Stokoe",
    author_email="keagan.stokoe@gmail.com",
    py_modules=["bibliocli"],
    install_requires=["Click", "requests", "rich"],
    entry_points={"console_scripts": "bib=bibliocli:bibliocli"},
)
