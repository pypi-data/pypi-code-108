#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'scanpy>=1.8.2', 'numpy>=1.20.0', 'pandas>=1.2.0' ]

test_requirements = [ ]

setup(
    author="Patrick Stumpf",
    author_email='stumpf@combine.rwth-aachen.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="PhysioSpace methods for python",
    entry_points={
        'console_scripts': [
            'pysiospace=pysiospace.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pysiospace',
    name='pysiospace',
    packages=find_packages(include=['pysiospace', 'pysiospace.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://git.rwth-aachen.de/pstumpf/pysiospace',
    version='0.1.7',
    zip_safe=False,
)
