#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages


def empty_or_comment(x):
    return len(x) == 0 or x.strip().startswith("#")


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as reqs:
    requirements = filter(empty_or_comment, reqs.read().splitlines())

with open('requirements_dev.txt') as reqs:
    dev_requirements = filter(empty_or_comment, reqs.read().splitlines())

setup(
    author="Aliaksandr Babrykovich",
    author_email='abobrikovich@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="""
        Python implementation of bibliography specification
        https://github.com/relaton/relaton-models#bibliography-uml-models
    """,
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords='relaton_bib',
    name='relaton_bib',
    packages=find_packages(include=['relaton_bib', 'relaton_bib.*']),
    test_suite='tests',
    tests_require=dev_requirements,
    url='https://github.com/relaton/relaton-bib-py',
    version='0.2.0',
    zip_safe=False,
)
