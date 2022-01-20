import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyfer",
    version="4.0.1",
    author="Elby Data",
    author_email="info@elbydata.com",
    description="Simple string encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elbydata/pyfer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
