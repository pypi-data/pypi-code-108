import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='idu',
    version='0.4.0',
    packages=['idu'],
    url='https://github.com/jftsang/idu',
    license='MIT License',
    author='J. M. F. Tsang',
    author_email='j.m.f.tsang@cantab.net',
    description='interactive disk usage analyser',
    long_description=README,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'idu=idu:main',
        ]
    },
)
