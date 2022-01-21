import setuptools
from setuptools import setup

NAME = "maintain_PlatoUtils"
VERSION = "0.1.2.70"
PY_MODULES = ["maintain_PlatoUtils"]

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=VERSION,
    py_modules=PY_MODULES,
    packages=setuptools.find_packages(),
    url='https://github.com/Timaos123/maintian_PlatoUtils.git',
    license='MIT',
    author='Timaos',
    author_email='201436009@uibe.edu.cn',
    description='运营PlatoDB的工具',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy',
                      "nebula-python",
                      "pandas",
                      "gensim",
                      "tensorflow",
                      "stellargraph",
                      "networkx",
                      "chardet"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
