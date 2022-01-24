from setuptools import setup, find_packages
from qpd_version import __version__


with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="qpd",
    version=__version__,
    packages=find_packages(),
    description="Query Pandas Using SQL",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    author="Han Wang",
    author_email="goodwanghan@gmail.com",
    keywords="pandas sql",
    url="http://github.com/goodwanghan/qpd",
    install_requires=[
        "pandas>=1.0.2",
        "triad",
        "adagio",
        "sqlalchemy",
        "antlr4-python3-runtime",
    ],
    extras_require={
        "dask": ["dask[dataframe]", "cloudpickle>=1.4.0"],
        "ray": ["pandas>=1.1.2", "modin[ray]>=0.8.1.1"],
        "all": ["dask[dataframe]", "cloudpickle>=1.4.0", "modin[ray]"],
    },
    classifiers=[
        # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.6",
)
