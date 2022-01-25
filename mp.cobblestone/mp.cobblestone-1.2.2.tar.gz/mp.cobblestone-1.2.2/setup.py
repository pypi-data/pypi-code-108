from setuptools import setup, find_packages

long_desc = open('README.md').read()

setup(
    packages=find_packages(),
    long_description=long_desc,
    long_description_content_type='text/markdown')
