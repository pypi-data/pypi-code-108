from setuptools import setup


with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()


setup(
    name="header-printer",
    version="0.0.7",
    description="Python package for printing a nicely formatted header.",
    author="Michał Wiśniewski",
    packages=["header_printer"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Michael-Wisniewski/header-printer",
    project_urls={
        "Documentation": "https://github.com/Michael-Wisniewski/header-printer",
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require = {
        "dev": [
            "black==21.12b0",
            "check-manifest==0.47",
            "coverage-badge==1.1.0",
            "flake8==4.0.1",
            "isort==5.10.1",
            "tox==3.24.5",
            "twine==3.7.1",
        ]
    },
)
