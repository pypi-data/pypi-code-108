from distutils.core import setup

from setuptools import find_packages

with open("resman_client/README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="resman-client",
    version="1.6",
    author="Tsing Jyujing",
    author_email="nigel434@gmail.com",
    description="Python client of Resman",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TsingJyujing/DataSpider",
    packages=[
        p
        for p in find_packages()
        if p.startswith("resman_client.") or p == "resman_client"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "python-magic",
        "pydantic",
        "requests-toolbelt",
        "click",
        "chardet"
    ],
    entry_points={
        'console_scripts': [
            'resman-cli=resman_client.cli:main',
        ],
    },
)
