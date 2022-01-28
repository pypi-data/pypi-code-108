from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='pyfbook',
    version='0.3.10',
    description='Easily collect data from Facebook APIs',
    long_description=readme,
    keywords='collect data facebook api',
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3',
    install_requires=[
        "dbstream>=0.0.14",
        "PyYAML>=5.1"
    ],
)
