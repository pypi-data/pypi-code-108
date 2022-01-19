from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="trading-strategy-qstrader",
    version="0.4",
    description="QSTrader backtesting simulation engine (forked)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tradingstrategy-ai/qstrader",
    author="Mikko Ohtamaa",
    author_email="mikko@capitalgram.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "Click>=7.1.2",
        "matplotlib>=3.0.3",
        "numpy>=1.18.4",
        "pandas>=1.1.5",
        "seaborn>=0.10.1"
    ]
)
