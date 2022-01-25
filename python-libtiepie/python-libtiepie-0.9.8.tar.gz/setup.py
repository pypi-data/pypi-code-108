#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='python-libtiepie',
      version='0.9.8',
      description='Python bindings for LibTiePie',
      license='MIT',
      author='TiePie engineering',
      author_email='support@tiepie.nl',
      url='https://github.com/TiePie/python-libtiepie',
      packages=find_packages(include=['libtiepie', 'libtiepie.*']),
      package_data={'libtiepie': ['_platform/*/*/*.dll']},
      python_requires='>=3',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows :: Windows 10',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development',
      ])
