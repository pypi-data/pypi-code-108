#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

def main():
  setuptools.setup(
    name                 = 'upbox',
    version              = '2022.01.19.2245',
    description          = 'uploading website and database system',
    long_description     = long_description(),
    url                  = 'https://github.com/wdbm/upbox',
    author               = 'Will Breaden Madden',
    author_email         = 'wbm@protonmail.ch',
    license              = 'GPLv3',
    packages             = setuptools.find_packages(),
    install_requires     = [
                           'dataset',
                           'Flask',
                           'technicolor'
                           ],
    entry_points         = {
                           'console_scripts': ('upbox=upbox.__init__:main')
                           },
    include_package_data = True,
    zip_safe             = False
  )

def long_description(filename='README.md'):
  if os.path.isfile(os.path.expandvars(filename)):
    try:
      import pypandoc
      long_description = pypandoc.convert_file(filename, 'rst')
    except ImportError:
      long_description = open(filename).read()
  else:
    long_description = ''
  return long_description

if __name__ == '__main__':
  main()
