import pathlib
from setuptools import setup, find_packages

setup(
    name="fcapsy-experiments",
    version="0.2.3",
    author="Tomáš Mikula",
    author_email="mail@tomasmikula.cz",
    description="Package of experiments for fcapsy library.",
    keywords="fca formal concept analysis experiments",
    license="MIT license",
    url="https://github.com/mikulatomas/fcapsy_experiments",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "fcapsy",
        "plotly",
        "pandas",
        "binsdpy",
        "sklearn",
        "fuzzycorr",
        "scipy",
        "numpy",
    ],
    long_description=pathlib.Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
