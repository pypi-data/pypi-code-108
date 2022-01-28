"""
Setup the Python package
"""

import pathlib
import re
from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

WORK_DIR = pathlib.Path(__file__).parent


def get_version():
    """ Get version """

    txt = (WORK_DIR / 'libdev' / '__init__.py').read_text('utf-8')

    try:
        return re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
    except IndexError as e:
        raise RuntimeError('Unable to determine version') from e


setup(
    name='libdev',
    version=get_version(),
    description='Set of standard functions for development',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kosyachniy/lib',
    author='Alexey Poloz',
    author_email='polozhev@mail.ru',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    keywords=(
        'standard, lib, dev, development, cfg, config, generate, codes, '
        'tokens, ids, passwords, generator, ciphers, time, formatter, nlp, '
        'natural language, aws, s3, upload file, file server'
    ),
    packages=find_packages(exclude=('tests',)),
    python_requires='>=3.7, <4',
    install_requires=[
        'python-dotenv==0.19.2',
        'boto3==1.20.31',
    ],
    project_urls={
        'Source': 'https://github.com/kosyachniy/lib',
    },
    license='MIT',
    include_package_data=False,
)
