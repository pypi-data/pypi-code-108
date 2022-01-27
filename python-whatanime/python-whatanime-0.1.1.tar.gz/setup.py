from setuptools import setup

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="python-whatanime",
    version="0.1.1",
    author="Joker Hacker",
    author_email="jokerhacker.6521@protonmail.com",
    packages=["WhatAnime"],
    description="An Unofficial python wrapper for trace.moe",
    license='License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Black-Bulls-Bots/WhatAnime",
    project_urls = {
        "Discussion" : "https://t.me/blackbulls_support",
    },
    install_requires=[
        "requests"
    ],
    python_requires = ">=3.9"
)