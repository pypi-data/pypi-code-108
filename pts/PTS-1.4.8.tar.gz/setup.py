import os
import re

import setuptools

from setuptools import setup

# A handful of variables that are used a couple of times.
github_url = 'https://github.com/TheElementalOfDestruction/pts'
main_module = 'PTS'

# Read in the description from README.
with open('README.rst', 'rb') as stream:
    long_description = stream.read().decode('utf-8').replace('\r', '')

# Get the version number (can't be imported because of requirements).
version_re = re.compile("__version__ = '(?P<version>[0-9\\.]*)'")
with open('PTS/__init__.py', 'r') as stream:
    contents = stream.read()
match = version_re.search(contents)
version = match.groupdict()['version']

# read in the dependencies from the virtualenv requirements file
dependencies = []
filename = os.path.join('requirements.txt')
with open(filename, 'r') as stream:
    for line in stream:
        package = line.strip().split('#')[0]
        if package:
            dependencies.append(package)

setup(
    name = main_module,
    version = version,
    description = "PIL Text Scaler",
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
    url = github_url,
    download_url = '{}/archives/master'.format(github_url),
    author = 'Destiny Peterson (The Elemental of Destruction)',
    author_email = 'arceusthe@gmail.com',
    license = 'GPL',
    packages = setuptools.find_packages(),
    py_modules = [main_module],
    include_package_data = True,
    install_requires = dependencies,
)
