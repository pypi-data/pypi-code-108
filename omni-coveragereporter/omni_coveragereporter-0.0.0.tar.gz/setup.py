# -*- coding: utf-8 -*-
from distutils.core import setup

from setuptools import find_packages

with open("README.txt", "r") as fh:
    long_description = fh.read()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    name='omni_coveragereporter',
    package_dir={'': 'src/omni_coveragereporter'},
    packages=find_packages(where='src/omni_coveragereporter'),
    py_modules=["omni_coveragereporter"],
    scripts=[
        'src/omni_coveragereporter/omni_coveragereporter_python.py',
        'src/omni_coveragereporter/codacy_client.py',
        'src/omni_coveragereporter/codacy_converter.py',
        'src/omni_coveragereporter/codecov_client.py',
        'src/omni_coveragereporter/codecov_converter.py',
        'src/omni_coveragereporter/coveragepy_parser.py',
        'src/omni_coveragereporter/coveralls_client.py',
        'src/omni_coveragereporter/coveralls_converter.py',
        'src/omni_coveragereporter/common.py',
    ],
    version='0.0.0',
    description='Omni Coverage Reporter. Strives to be as universal as possible in receiving, converting and sending reports from many types to different online API''s',
    author='João Esperancinha',
    author_email='jofisaes@gmail.com',
    url='http://joaofilipesabinoesperancinha.nl/main',
    keywords=['report', 'codacy', 'coveralls', 'codecov'],
    install_requires=[
        # 'math',
        # 'random',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
