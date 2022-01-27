import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sasdbpy",
    version="0.0.8",
    author="Cereddy",
    author_email="nacer.htag@gmail.com",
    description="A helper class for reading sas7bdat database files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cereddy/sasdbpy",
    project_urls={
        "Bug Tracker": "https://github.com/cereddy/sasdbpy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "./"},
    packages=setuptools.find_packages(where="./"),
    install_requires=[
            "numpy",
            "pandas",
            "sas7bdat"],
    python_requires=">=3.6",
)