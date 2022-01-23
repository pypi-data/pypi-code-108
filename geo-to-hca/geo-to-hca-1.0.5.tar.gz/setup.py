import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()
install_requires = [line.rstrip() for line in (HERE / "requirements.txt").read_text().splitlines()]

setup(
    name="geo-to-hca",
    version="1.0.5",
    description="A tool to assist in the automatic conversion of geo metadata to hca metadata standard",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ebi-ait/geo_to_hca",
    author="Ami Day, Alegria Aclan, Enrique Sapena Ventura, Wei Kheng Teh",
    author_email="ami@ebi.ac.uk, aaclan@ebi.ac.uk, enrique@ebi.ac.uk, wteh@ebi.ac.uk",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "geo-to-hca=geo_to_hca.geo_to_hca:main",
        ]
    },
)
