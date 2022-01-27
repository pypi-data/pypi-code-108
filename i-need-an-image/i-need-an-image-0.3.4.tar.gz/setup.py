from setuptools import setup

with open('requirements.txt', 'r') as f:
    requirements = [line for line in f.readlines()]

setup(
    install_requires=requirements
)
