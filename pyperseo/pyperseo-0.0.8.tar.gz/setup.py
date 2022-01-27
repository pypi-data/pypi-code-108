# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="pyperseo",
    version="0.0.8",
    packages= ['pyperseo'],                           #find_packages(),
    author="Pablo Alarcón Moreno",
    author_email="pabloalarconmoreno@gmail.com",
    url="https://github.com/pabloalarconm/PERSEO",
    description="Personal Semantic Objects",
    license="MIT",
    keywords=["Semantics", "RDF", "FAIR", "EJP"],
    long_description=readme
)