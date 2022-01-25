# Import required functions
from setuptools import setup, find_packages

# Call setup function
setup(
    author="Javad Ebadi, Vahid Hoseinzade",
    author_email="javad.ebadi.1990@gmail.com, vahid.hoseinzade64@gmail.com",
    description="A simple python wrapper for inspirehep API",
    name="pyinspirehep",
    packages=find_packages(include=["pyinspirehep", "pyinspirehep.*"]),
    version="0.1.0",
    install_requires=['requests'],
    python_requires='>=3',
)
