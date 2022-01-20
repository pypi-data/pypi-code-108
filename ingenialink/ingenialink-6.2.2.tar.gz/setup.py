#!/usr/bin/env python

import re
from setuptools import setup
from distutils.cmd import Command
import shutil
import os

_version = re.search(r'__version__\s+=\s+\'(.*)\'',
                     open('ingenialink/__init__.py').read()).group(1)


def get_docs_url():
    return "https://distext.ingeniamc.com/doc/ingenialink-python/{}".format(_version)


class BDistAppCommand(Command):
    """Custom command to build the application."""

    description = 'Build the application'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Copying dlls...")
        shutil.copy('resources/Packet.dll', 'ingenialink/')
        shutil.copy('resources/wpcap.dll', 'ingenialink/')


class BCleanAppCommand(Command):
    """Custom command to clean the application."""

    description = 'Clean the application'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Cleaning files...")
        if os.path.exists("ingenialink/Packet.dll"):
            os.remove("ingenialink/Packet.dll")
        if os.path.exists("ingenialink/wpcap.dll"):
            os.remove("ingenialink/wpcap.dll")


setup(name='ingenialink',
      version=_version,
      packages=['ingenialink', 'ingenialink.canopen', 'ingenialink.ethercat',
                'ingenialink.ethernet', 'ingenialink.serial', 'ingenialink.ipb',
                'ingenialink.utils'],
      description='IngeniaLink Communications Library',
      long_description=open('README.rst').read(),
      author='Ingenia Motion Control',
      author_email='support@ingeniamc.com',
      url='https://www.ingeniamc.com',
      project_urls={
          'Documentation': get_docs_url(),
          'Source': 'https://github.com/ingeniamc/ingenialink-python'
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: C',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: Communications',
          'Topic :: Software Development :: Libraries'
      ],
      cmdclass={
        'bdist_app': BDistAppCommand,
        'bclean_app': BCleanAppCommand
      },
      setup_requires=['cffi==1.14.6'],
      cffi_modules=['ingenialink/ingenialink_build.py:ffibuilder'],
      install_requires=[
          'cffi==1.14.6',
          'numpy<=1.19.5',
          'canopen>=1.0.0',
          'ingenialogger>=0.2.1'
      ],
      include_package_data = True

      )
