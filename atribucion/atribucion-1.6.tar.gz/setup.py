from setuptools import find_packages, setup
from os import path
from codecs import open

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='atribucion',
    version='1.6',
    description='Libreria para correr modelos de atribucion para marketing',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tomasrene/atribucion",
    author="Tomas Reneboldi",
    author_email="tomasrene@gmail.com",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(include=['atribucion']),
    install_requires=['pandas','numpy']
)