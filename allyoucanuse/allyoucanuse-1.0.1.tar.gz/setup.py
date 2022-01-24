import setuptools
from numpy import where

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="allyoucanuse",
    version="1.0.1",
    author="diebridge",
    author_email="f_flare@live.cn",
    description="One-liners of everything - a hodge-podge of python tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kunlubrain/allyoucanuse",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
