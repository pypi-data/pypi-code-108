from setuptools import setup, find_packages
from os import path
from io import open


# with open("README.rst", "r", encoding='utf-8') as fh:
#     long_description = fh.read()

with open('LICENSE', "r", encoding='utf-8') as f:
    license = f.read()

# LONG_DESCRIPTION = """\
# Test text copied from seaborn
# Seaborn is a library for making statistical graphics in Python. It is built on top of `matplotlib <https://matplotlib.org/>`_ and closely integrated with `pandas <https://pandas.pydata.org/>`_ data structures.
# Here is some of the functionality that seaborn offers:
# - A dataset-oriented API for examining relationships between multiple variables
# - Specialized support for using categorical variables to show observations or aggregate statistics
# - Options for visualizing univariate or bivariate distributions and for comparing them between subsets of data
# - Automatic estimation and plotting of linear regression models for different kinds dependent variables
# - Convenient views onto the overall structure of complex datasets
# - High-level abstractions for structuring multi-plot grids that let you easily build complex visualizations
# - Concise control over matplotlib figure styling with several built-in themes
# - Tools for choosing color palettes that faithfully reveal patterns in your data
# Seaborn aims to make visualization a central part of exploring and understanding data. Its dataset-oriented plotting functions operate on dataframes and arrays containing whole datasets and internally perform the necessary semantic mapping and statistical aggregation to produce informative plots.
# """

setup(
    version='0.0.7',
    name='streng',
    description='structural engineering tools with python',
    # long_description=LONG_DESCRIPTION,
    # long_description_content_type="text/markdown",
    author='panagop',
    author_email="giorgos@panagop.com",
    url=r'https://github.com/gpanagop/streng',
    license=license,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    packages=find_packages(exclude=('testing', 'docs')),
    install_requires=[
        'tabulate', 'numpy', 'matplotlib', 'pandas', 'sympy', 'scipy', 'sqlalchemy'],
)