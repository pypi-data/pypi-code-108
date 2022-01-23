import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="verbosemanager",
    version="1.2.0",
    author="Alex H. Room",
    author_email="alex.room@btinternet.com",
    description="A library for managing verbose output on complex processes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexhroom/verbosemanager",
    project_urls={
        "Bug Tracker": "https://github.com/alexhroom/verbosemanager/issues",
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

