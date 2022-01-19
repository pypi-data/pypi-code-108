#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as file:
    long_description_ = file.read()
    
setuptools.setup(
    name="tokenspan",
    version="0.6.0",
    author="François Konschelle - IAM CHU Bordeaux France",
    author_email="via.issue@only.please",
    description="Basic tools to tokenize (i.e. to construct atomic-entities/sub-strings of) a string, for Natural Language Processing (NLP). Usefull also for annotation, tree parsing, entity linking, ... (in fact, anything that links a string or its sub-parts to an other object). Key concepts are versatility to other librairies, and freedom to define many concepts on top of a string.",
    long_description=long_description_,
    long_description_content_type="text/markdown",
    license="GNU GENERAL PUBLIC LICENSE v.3",
    url="https://framagit.org/nlp/tokenspan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.7',
)
