#!/usr/bin/env python3

from setuptools import setup, find_packages
import versioneer

with open('README.md') as f:
    readme = f.read()

dependencies = []
with open('requirements.txt', 'r') as f:
    for line in f:
        dependencies.append(line.strip())

setup(
    name='snppy',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Codebase for running common variant association analyses.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Tarjinder Singh',
    author_email='tsingh@broadinstitute.org',
    url='https://github.com/alpha-team-genetics/snppy',
    license='MIT license',
    python_requires='>=3.7',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=dependencies
)