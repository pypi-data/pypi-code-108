from setuptools import setup, find_packages
from os.path import join, dirname
import welltest

setup(
    name='welltest',
    version=welltest.__version__,
    description='Simple welltest functions for transient pressure analysis calculations in petroleum engineering',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    url='https://github.com/khabibullinra/welltest-functions',
    author='Rinat Khabibullin',
    author_email='khabibullinra@gmail.com',
    license='BSD 3-Clause License',
    install_requires=[
          'numpy', 'anaflow', 
      ],
    test_suite='tests',
)