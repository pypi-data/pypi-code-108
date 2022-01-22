import subprocess

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cry-vs.py",
    version="0.0.0.5",
    author="addikted",
    # author_email="author@example.com",
    description="A Crypto-Versus wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AW1534/cry-vs.py",
    project_urls={
        "Bug Tracker": "https://github.com/AW1534/cry-vs.py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.27.1"
    ]
)