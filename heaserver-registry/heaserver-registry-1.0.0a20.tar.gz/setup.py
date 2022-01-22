"""
Documentation for setup.py files is at http://setuptools.readthedocs.io/en/latest/setuptools.html
"""

import setuptools

# Import the README.md file contents
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='heaserver-registry',
                 version='1.0.0a20',
                 description='The HEA registry service.',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 url='https://risr.hci.utah.edu',
                 author='Research Informatics Shared Resource, Huntsman Cancer Institute, Salt Lake City, UT',
                 author_email='Andrew.Post@hci.utah.edu',
                 python_requires='>=3.8',
                 package_dir={'': 'src'},
                 packages=['heaserver.registry'],
                 package_data={'heaserver.registry': ['wstl/*.json']},
                 install_requires=[
                     'heaserver>=1.0.0a44, < 1.0.0a45'
                 ],
                 classifiers=[
                     'Development Status :: 2 - Pre-Alpha',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: Apache Software License',
                     'Framework :: AsyncIO',
                     'Environment :: Web Environment',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.8',
                     'Topic :: Software Development',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Scientific/Engineering :: Bio-Informatics',
                     'Topic :: Scientific/Engineering :: Information Analysis',
                     'Topic :: Scientific/Engineering :: Medical Science Apps.'
                 ],
                 entry_points={
                     'console_scripts': [
                         'heaserver-registry = heaserver.registry.service:main'
                     ]
                 }
                 )
