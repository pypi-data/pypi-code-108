from pathlib import Path
from setuptools import setup, find_packages

PARENT_DIR = Path(__file__).resolve().parent

setup(
    name="up42-blockutils",
    version=PARENT_DIR.joinpath("blockutils/_version.txt").read_text(),
    author="UP42",
    author_email="support@up42.com",
    description="Block development toolkit for UP42",
    long_description=PARENT_DIR.joinpath("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://www.up42.com",
    packages=find_packages(exclude=("tests", "docs")),
    package_data={"": ["_version.txt"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=PARENT_DIR.joinpath("requirements.txt").read_text().splitlines(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7, <3.10",
)
