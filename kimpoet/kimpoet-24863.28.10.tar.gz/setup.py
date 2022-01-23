# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 00:24:28 2022

@author: 86183
"""

from setuptools import setup
from setuptools import find_packages
setup(
      name="kimpoet",
      version="24863.28.10",
      description="the package is used to define poets",
      classifiers=[
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10'
          ],
      author="pycreaterset",
      author_email="13816349024@139.com",
      url='',
      long_discription='''
      the package is used to define poets
      you can define poets like libai and dufu
      ''',
      packages=find_packages('src'),
      package_dir = {'':'src'},         # 必填
      include_package_data = True,
      )
