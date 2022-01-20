import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sparkcleaner",
    version="1.1.1",
    author="IvoW",
    author_email="ivownds@gmail.com",
    description="cleaning functions for pyspark df",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IvoWnds/pysparkdfcleaner",
    project_urls={
        "Bug Tracker": "https://github.com/IvoWnds/pysparkdfcleaner/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
