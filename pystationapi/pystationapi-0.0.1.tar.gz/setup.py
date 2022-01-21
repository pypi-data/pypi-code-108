from setuptools import setup,find_packages


setup(
    name='pystationapi',
    version='0.0.1',
    author='Giacomo Lorenzo',
    author_email='giacomolinux@gmail.com',
    url='http://pypi.python.org/pypi/pystation-api/',
    license='Apache License 2.0',
    description='Get games from playstation api based on graphql',
    packages=find_packages(),
    install_requires=[''],
    test_suite='pystationapi.tests'
)