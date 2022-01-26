from setuptools import setup, find_packages
from grutils import __author__, __version__, __email__

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requirementPath = this_directory + '/requirements.txt'
install_requires = []
with open(requirementPath) as f:
    install_requires = f.read().splitlines()

setup(
    name='grutils',
    version=__version__,
    author=__author__,
    author_email=__email__,
    license='Apache2.0',
    description='reusable grutils',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=install_requires,
    project_urls={
        'Source': 'https://github.com/lldld/gr.py3.utils'
    },
)
