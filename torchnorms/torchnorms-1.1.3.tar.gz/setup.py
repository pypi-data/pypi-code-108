import setuptools
import os

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="torchnorms", #
    version="1.1.3",
    author="Pasquale Minervini, Erik Arakelyan",
    author_email="",
    description="Differentiable Fuzzy Logic operators for ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pminervini/torch-norms",
    packages=setuptools.find_packages(),
    # package_dir={"": "torchnorms"},
    install_requires=[],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
)
