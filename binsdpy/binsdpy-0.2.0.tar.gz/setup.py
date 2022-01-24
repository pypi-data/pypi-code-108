import pathlib
from setuptools import setup, find_packages
from binsdpy import __version__, __author__, __email__, __license__

setup(
    name="binsdpy",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Python implementation of binary similarity and distance measures.",
    keywords="binary similarity distance measure",
    license=__license__,
    url="https://github.com/mikulatomas/binsdpy",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["bitsets", "numpy"],
    extras_require={
        'test': ['pytest', 'pytest-cov'],
    },
    long_description=pathlib.Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
