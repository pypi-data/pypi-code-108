import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup_info = {
    "name": "moneysuffixes",
    "version": "1.0.2",
    "author": "CantCode",
    "author_email": "cantcode023@gmail.com",
    "description": "Shortens long amount of number.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "url": "https://github.com/CantCode023/MoneySuffixes",
    "packages": setuptools.find_packages(),
    "classifiers": [
        "Programming Language :: Python :: 3",
    ],
    "python_requires": '>=3.7'
}


setuptools.setup(**setup_info)