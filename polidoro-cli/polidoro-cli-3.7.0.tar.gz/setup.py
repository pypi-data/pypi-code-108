"""
Setup to create the package
"""
import polidoro_cli
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='polidoro-cli',
    version=polidoro_cli.VERSION,
    description='Polidoro CLI.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/heitorpolidoro/polidoro-cli',
    author='Heitor Polidoro',
    scripts=['bin/cli'],
    license='unlicense',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    install_requires=['polidoro-argument >= 3.4', 'pyyaml'],
    include_package_data=True
)
