#!/usr/bin/env python
'''
Setup script for the lib99ocl package
'''

__author__ = 'Marcos Romero Lamas'
__email__ = 'marromlam@gmail.com'
__license__ = 'MIT License Copyright (c) 2021 Marcos Romero Lamas'


# Modules {{{

import os
import sys
import setuptools
import subprocess
import textwrap

# }}}


# Class {{{

class CheckFormatCommand(setuptools.Command):
    '''
    Check the format of the files in the given directory. This script takes only
    one argument, the directory to process. A recursive look-up will be done to
    look for python files in the sub-directories and determine whether the files
    have the correct format.
    '''
    description = 'check the format of the files of a certain type in a given directory'

    user_options = [
        ('directory=', 'd', 'directory to process'),
        ('file-type=', 't', 'file type (python|all)'),
    ]

    def initialize_options(self):
        '''
        Running at the begining of the configuration.
        '''
        self.directory = None
        self.file_type = None

    def finalize_options(self):
        '''
        Running at the end of the configuration.
        '''
        if self.directory is None:
            raise Exception('Parameter --directory is missing')
        if not os.path.isdir(self.directory):
            raise Exception('Not a directory {}'.format(self.directory))
        if self.file_type is None:
            raise Exception('Parameter --file-type is missing')
        if self.file_type not in ('python', 'all'):
            raise Exception('File type must be either "python" or "all"')

    def run(self):
        '''
        Execution of the command action.
        '''
        matched_files = []
        for root, _, files in os.walk(self.directory):
            for f in files:
                if self.file_type == 'python' and not f.endswith('.py'):
                    continue
                matched_files.append(os.path.join(root, f))

        process = subprocess.Popen(['autopep8', '--diff'] + matched_files,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if process.returncode < 0:
            raise RuntimeError('Call to autopep8 exited with error {}\nMessage:\n{}'.format(
                abs(returncode), stderr))

        if len(stdout):
            raise RuntimeError(
                'Found differences for files in directory "{}" with file type "{}"'.format(self.directory, self.file_type))

# }}}


# Version {{{
# Version of the package. Before a new release is made just the version_list
# must be changed. The options for the fourth tag are "dev", "alpha", "beta"
# and "final".
version_list = [0, 0, 0, 'dev', 8]

VERSION = f"{version_list[0]}.{version_list[1]}.{version_list[2]}"

tag = version_list[3]
if tag != 'final':
  if tag in ('alpha', 'beta', 'dev'):
    VERSION += f"{tag}{version_list[-1]}"
  else:
    raise ValueError(f'Unable to parse version tuple {version_list}')

# }}}


# Helpers {{{

def create_version_file():
    '''
    Create the file version.py given the version of the package.
    '''
    version_file = open('lib99ocl/version.py', 'wt')
    version_file.write(textwrap.dedent("""\
    '''
    Auto-generated module holding the version of the lib99ocl package
    '''

    VERSION = "{}"
    VERSION_INFO = {}

    __all__ = ['VERSION', 'VERSION_INFO']
    """.format(VERSION, version_list)))
    version_file.close()


def install_requirements():
  '''
  Read installation requirements from "requirements.txt" file.
  '''
  requirements = []
  with open('requirements.txt') as f:
    for line in f:
      li = line.strip()
      if not li.startswith('#'):
        requirements.append(li)
  return requirements

# }}}


# Setup package {{{

def setup_package():
  '''
  Set up the package.
  '''

  metadata = dict(
      name='lib99ocl',
      version=VERSION,
      author=__author__,
      author_email=__email__,
      url='https://github.com/marromlam/py-lib99ocl.git',
      download_url='https://github.com/marromlam/py-lib99ocl.git',
      install_requires=install_requirements(),
      python_requires='>=3.5',
      license=__license__,
      description='OpenCL C99 library',
      long_description=open('README.rst').read() + "\n\n" + __license__,
      long_description_content_type = 'text/x-rst',
      platforms=['Linux', 'macOS', 'Windows'],
      keywords='computational physics',
      cmdclass={'check_format': CheckFormatCommand},
      # package_dir={'lib99ocl': 'lib99ocl'},
      include_package_data=True,
      # package_data={"lib99ocl":["lib99ocl/*"]},
      packages=['lib99ocl']
  )
  create_version_file()
  setuptools.setup(**metadata)


if __name__ == '__main__':
  setup_package()

# }}}


# vim:foldmethod=marker
