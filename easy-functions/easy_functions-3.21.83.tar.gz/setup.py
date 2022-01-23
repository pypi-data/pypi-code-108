from setuptools import setup
from easy_functions import __version__ as v

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
    name = 'easy_functions',
    version = v,
    py_modules = ['easy_functions'],
    author = 'Jerry0940',
    author_email = 'j13816180940@139.com',
    license = 'MIT',
    description = '一个简单小巧但实用的模块',
    long_description = long_description,
    url = 'https://github.com/MCTF-Alpha-27/easy_functions',
    long_description_content_type = 'text/markdown',
    classifiers = [
       "Programming Language :: Python :: 3"
    ],
)