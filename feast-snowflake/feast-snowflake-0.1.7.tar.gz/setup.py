# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

INSTALL_REQUIRE = [
    "feast>=0.17.*",
    "snowflake-connector-python[pandas]>=2.6.*",
]

setup(
    name="feast-snowflake",
    version="0.1.7",
    author="Miles Adkins",
    author_email="miles.adkins@snowflake.com",
    description="Snowflake offline store for Feast",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.7.0",
    url="https://github.com/sfc-gh-madkins/feast-snowflake",
    project_urls={
        "Bug Tracker": "https://github.com/sfc-gh-madkins/feast-snowflake/issues",
    },
    license='Apache License, Version 2.0',
    packages=["feast_snowflake", ],
    install_requires=INSTALL_REQUIRE,
    keywords=("feast featurestore snowflake offlinestore"),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
