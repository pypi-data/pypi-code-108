from setuptools import find_packages, setup
import codecs
import os


STANDARD = 'utf-8'
NAME = 'pinn-ics'
VERSION = '1.0.2'
DESCRIPTION = 'Solving physics problems by using Deep Learning'
README_NAME = 'README.md'
AUTHOR = 'threezinedine'

with codecs.open(README_NAME, encoding=STANDARD) as fh:
    LONG_DESCRIPTION = "\n" + fh.read()

classifiers = [
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3 :: Only"
]


setup(
    name='pinn-ics',
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=LONG_DESCRIPTION,
    author_emal='threezinedine@gmail.com',
    packages=find_packages(),
    requires=['tensorflow', 'numpy'],
    keywords=['python', 'scientist', "equation solver"],
    classifiers=classifiers
)
