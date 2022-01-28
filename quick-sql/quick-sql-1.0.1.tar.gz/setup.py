import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quick-sql",
    version="1.0.1",
    author="Kishcods",
    author_email="kisshancods@protonmail.com",
    description="A python library for sqlite3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "quick_sqlite"},
    packages=setuptools.find_packages(where="quick_sqlite"),
    python_requires=">=3.7",
)