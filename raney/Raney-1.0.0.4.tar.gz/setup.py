# 30/04/2021

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="Raney",
    version="1.0.0.4",
    author="R0htg0r",
    author_email="osvaldo.pedreiro.ecaminhoneiro@gmail.com",
    url="https://github.com/R0htg0r",
    description="Essa biblioteca foi desenvolvida para ser mais fácil a criação de combinações rápidas.",
    long_description=README,
    long_description_content_type="text/markdown",

    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
    keywords=['Python3', 'Python2', 'Python', 'Raney', 'Password', 'Combinações', "API Password"],
    packages=find_packages(),
)