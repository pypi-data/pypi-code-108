from gettext import install
from unicodedata import name
from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='printf 1',
    version='0.0.1',
    description='this a print modifier',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='jaideep kalagara',
    author_email='',
    license='MIT',
    classifiers=classifiers,
    keywords='printf',
    packages=find_packages(),
    insall_requires = ['']
)