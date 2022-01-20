from unicodedata import name
from setuptools import setup, find_packages

classifiers = [
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python '
]

setup(
    name= 'sortingalgo',
    version= '0.0.1',
    description='Sorts the Given array', 
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    author='Sabhya Mittal',
    author_email = 'sabhyamittal26@gmail.com',
    url='',
    packages=find_packages(),
    classifiers=classifiers,
    license='MIT',
    keywords='Sorting',
    install_requires=['']
)