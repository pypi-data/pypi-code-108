import setuptools
from setuptools import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="bnptool",
    version="1.0.1a",
    author="linktlh",
    author_email="linktlh@gmail.com",
    description="A simple Commandline interface to create BNPs using BCML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linktlh/bnptool",
    include_package_data=True,
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts":
            ['bnptool = bnptool.__main__:main']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.7",
    install_requires=['bcml>=3.0.0'],
)
