from pathlib import Path
import setuptools

setuptools.setup(
    name='rudypdf',
    version=0.1,
    long_description=Path('README.md').read_text(),
    packages=setuptools.find_packages(exclude=['data', 'tests'])
)
