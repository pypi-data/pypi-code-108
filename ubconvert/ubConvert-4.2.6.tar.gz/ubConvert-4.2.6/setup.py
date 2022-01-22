from setuptools import setup
from os import path

fname = "c:\\users\\mount\\source\\repos\\mydashboard\\pypi\\ubconvert\\READIT.txt"

with open(fname, "r") as f:
    long_desc = f.read()



setup(
    name='ubConvert',
    version='4.2.6',
    author='ZennDogg',
    author_email='zenndogg@outlook.com.com',
    url='http://pypi.python.org/pypi/ubConvert/',
    license='LICENSE.txt',
    description='Units Converter Package',
    python_requires = '>=3.8',
    long_description = long_desc,
    long_description_content_type='text/markdown',

)
