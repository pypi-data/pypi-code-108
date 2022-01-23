import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqltables",
    version="1.5",
    author="Bob Pepin",
    author_email="pypi@pepin.io",
    description="SQL tables as first-class objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Source": "https://github.com/bobpepin/sqltables",
        "Documentation": "https://sqltables.readthedocs.io"
    },
    url="https://github.com/bobpepin/sqltables",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
