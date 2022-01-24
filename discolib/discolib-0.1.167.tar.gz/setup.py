#
# DISCo Python interface library
# Copyright (c) 2021 Greg Van Aken
#


import setuptools
import discolib
import os

SETUP_PATH = os.path.dirname(__file__)

with open(os.path.join(SETUP_PATH, 'requirements.txt')) as req_f:
    REQUIRED = req_f.read().splitlines()

with open('README.md', 'r') as readme:
    full_description = readme.read()

setuptools.setup(
    name='discolib',
    version=discolib.__version__,
    author='Greg Van Aken',
    author_email='gavanaken@gmail.com',
    description='A library for creating high-level interfaces to DISCo-conformant components',
    long_description=full_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gavanaken/disco',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    license="MIT",
    install_requires=REQUIRED
)
