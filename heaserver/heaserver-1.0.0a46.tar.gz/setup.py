"""
Documentation for setup.py files is at https://setuptools.readthedocs.io/en/latest/setuptools.html
"""

from setuptools import setup, find_namespace_packages


# Import the README.md file contents
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='heaserver',
      version='1.0.0a46',
      description='The server side of HEA.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://risr.hci.utah.edu',
      author='Research Informatics Shared Resource, Huntsman Cancer Institute, Salt Lake City, UT',
      author_email='Andrew.Post@hci.utah.edu',
      python_requires='>=3.8',
      package_dir={'': 'src'},
      packages=find_namespace_packages(where='src'),
      package_data={'heaserver.service': ['py.typed']},
      install_requires=[
          'heaobject~=1.0.0a18',
          'aiohttp[speedups]~=3.6.2',
          'aiohttp-remotes~=0.1.2',
          'motor~=2.1.0',
          'pytz~=2021.1',
          'tzlocal~=2.1',
          'uritemplate~=3.0.1',
          'accept-types~=0.4.1',
          'mongoquery~=1.3.6',
          'jsonschema~=3.2.0',
          'jsonmerge~=1.7.0',
          'requests>=2.20',
          'types-requests>=2.20',  # Should be set at same version as requests.
          'boto3==1.20.29',
          'botocore==1.23.29'
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Software Development',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Medical Science Apps.'
      ]
      )
