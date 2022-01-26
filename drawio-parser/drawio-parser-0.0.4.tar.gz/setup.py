import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="drawio-parser",
    version="0.0.4",
    author="Rafael Freire",
    author_email="rafaeldemaio@gmail.com",
    description="A drawio file parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Issues Tracker": "https://git.cvc.com.br/architecture/backend-platform/libraries/python/drawio-parser/issues",
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

