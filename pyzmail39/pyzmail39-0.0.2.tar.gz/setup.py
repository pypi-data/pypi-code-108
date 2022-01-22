import sys, os, shutil
import setuptools
from setuptools import setup, find_packages
    

setup(name='pyzmail39',
      version="0.0.2", 
      author='m63',
      author_email='m63.dev@gmail.com',
      url='http://www.magiksys.net/pyzmail',
      keywords= 'email',
      description='Python easy mail library, to parse, compose and send emails',
      long_description='This is a fork of pyzmail modified to be '
                       'pip-installable on Python 3.9',
      license='LGPL',
      packages=[ 'pyzmail'],
      test_suite = 'pyzmail.tests',
      scripts=[ 'scripts/pyzsendmail', 'scripts/pyzinfomail' ],
      classifiers=["Intended Audience :: Developers",
                  "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)", 
                  "Operating System :: OS Independent",
                  "Topic :: Communications :: Email",
                  "Topic :: System :: Networking",
                  "Topic :: Internet",
                  "Intended Audience :: Developers",
                  "Programming Language :: Python",                  
                  "Programming Language :: Python :: 3",
                  ],)
