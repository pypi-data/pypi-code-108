from distutils.core import setup
from setuptools import find_packages

setup(
    # Application name:
    name="onboardbase",

    # Version number (initial):
    version="0.0.1.dev1",

    # Application author details:
    author="Ernest Offiong",
    author_email="ernest.offiong@gmail.com",

    # Packages
    packages=find_packages(include=["onboardbase", "onboardbase.*"]),

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/onboardbase_v001/",

    license="MIT",
    python_requires='>=3',
    description="Onboardbase python sdk",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "requests",
        "pycryptodome",
        "PyYAML"
    ],

)