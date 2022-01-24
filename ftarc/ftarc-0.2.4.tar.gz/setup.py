#!/usr/bin/env python

from setuptools import find_packages, setup

from ftarc import __version__

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='ftarc',
    version=__version__,
    author='Daichi Narushima',
    author_email='dnarsil+github@gmail.com',
    description=(
        'FASTQ-to-analysis-ready-CRAM Workflow Executor'
        ' for Human Genome Sequencing'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dceoy/ftarc',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'docopt', 'jinja2', 'luigi', 'pip', 'psutil', 'pyyaml', 'shoper'
    ],
    entry_points={
        'console_scripts': ['ftarc=ftarc.cli.main:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    python_requires='>=3.6',
)
