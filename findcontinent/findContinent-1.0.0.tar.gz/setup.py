import os
from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='findContinent',
      version='1.0.0',
      description='This module can help you to get the continent of different countries',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/meShubhamJha/getconti',
      author='Shubham Jha',
      author_email='sjha0090@gmail.com',
      license='MIT',
      packages=['getconti'],
      python_requires='>3.5.2',
      install_requires=['pandas'],
      classifiers = [
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent"],
      include_package_data=True,
      zip_safe=False)