import setuptools
from distutils.core import setup

# read in the contents of the README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ThreadFixProAPI',
    version='1.0.12',
    packages=['ThreadFixProApi', '_utils',],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/x-rst'
)
