
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bajra",
    version="0.0.1",
    author="Souvik Pratiher",
    author_email="spratiher9@gmail.com",
    description="A efficient raw SQL ORM",
    url="https://github.com/Spratiher9/Bajra",
    download_url="https://github.com/Spratiher9/Bajra/archive/refs/tags/v0.0.1.tar.gz",
    keywords=['sql', 'orm', 'raw-sql', 'python', 'postgres', 'mysql', 'database'],
    packages=find_packages(),
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["bajra"],                   # Name of the python package
    install_requires=[
        "PyMySQL==0.9.2",
        "psycopg2-binary==2.9.3"
    ]                                       # Install other dependencies if any
)
