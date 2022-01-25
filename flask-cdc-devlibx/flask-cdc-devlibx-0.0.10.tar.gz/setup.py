#! /usr/bin/env python

import setuptools

with open('HISTORY.rst') as f:
    history = f.read()

description = 'Python DSL for setting up Flask app CDC'

setuptools.setup(
    name='flask-cdc-devlibx',
    version="0.0.10",
    description='{0}\n\n{1}'.format(description, history),
    long_description_content_type="text/markdown",
    long_description=open("README.md").read(),
    author='devlibx',
    author_email='devlibxgithub@gmail.com',
    url='https://github.com/devlibx/flask-cdc',
    packages=['flask_cdc'],
    package_dir={"": "."},
    license='MIT',
    install_requires=['kafka-python']
)
