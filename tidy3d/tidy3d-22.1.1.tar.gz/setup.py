from setuptools import setup, find_packages
import codecs
import os.path

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='tidy3d',
    version=get_version("tidy3d/__init__.py"),
    description='A Python API for Tidy3D FDTD Solver',
    author='FlexCompute, Inc.',
    author_email='lei@flexcompute.com',
    packages=find_packages(),
    install_requires=['aws-requests-auth', 'bcrypt'] + requirements,
    dependency_links=['http://github.com/flexcompute/warrant/tarball/master#egg=warrant-0.6.4'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
