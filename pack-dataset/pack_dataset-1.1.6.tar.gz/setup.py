from setuptools import setup

with open("README.rst") as f:
    long_description = f.read()

setup(
    name='pack_dataset',
    version='1.1.6',
    packages=['pack_dataset'],
    url='https://github.com/lnetw/pack_dataset',
    license='MIT License (MIT)',
    author='Maxim Ermak',
    author_email='',
    long_description=long_description,
    install_requires=["pandas == 1.3.4", "pymssql == 2.2.1", "hvac == 0.11.2"],
    classifiers=["Programming Language :: Python :: 3.8"],
    description='This project contains a loader of a special data set, as a connection to the database using pymssql'
)
