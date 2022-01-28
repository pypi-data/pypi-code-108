from setuptools import setup, find_packages

setup(
    name='fred_matt_merman',
    url='https://github.com/matt-merman',
    author='Mattia Di Battista',
    author_email='geom.dibattistamattia@gmail.com',
    # Needed to actually package something
    packages=find_packages(),
    # Needed for dependencies
    install_requires=['numpy', 'requests', 'pandas', 'matplotlib'],
    version='0.4',
)