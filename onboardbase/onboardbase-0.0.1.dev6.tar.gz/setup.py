from distutils.core import setup
from setuptools import find_packages

setup(
  # Application name:
  name="onboardbase",

  # Version number (initial):
  version="0.0.1.dev6",

  # Application author details:
  author="Ernest Offiong",
  author_email="ernest.offiong@gmail.com",

  # Packages
  packages=["onboardbase", "onboardbase.utils"],

  # Include additional files into the package
  include_package_data=True,

  # Details
  url="http://pypi.python.org/pypi/onboardbase_v001.dev6/",

  license="MIT",
  python_requires='>=3',
  description="Onboardbase python sdk",

  # long_description=open("README.txt").read(),

  # Dependent packages (distributions)
  install_requires=[
      "requests",
      "pycryptodome",
      "PyYAML"
  ],

  classifiers=[
    # 'Development Status :: 3 - Alpha',   
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],

)