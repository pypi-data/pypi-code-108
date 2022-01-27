#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 10:47:40 2019

@author: benjamin
"""

from setuptools import setup, find_packages

setup(name='spychhiker',
      version='0.8.11',
      description='Various python class for speech analysis and speech synthesis',
      url=' https://gitlab.com/benjamin.elie/spychhiker',
      author='Benjamin Elie',
      author_email='bnjmn.elie@gmail.com',
      license='CeCILL',
      packages=find_packages(),
      install_requires=[
          'h5py',
        'numpy',
        'matplotlib',
        'scipy',
        'statsmodels',
        'librosa',
        'praat-parselmouth',
        'scikit-learn',
        'tqdm'
    ],
      zip_safe=False)
