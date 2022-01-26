"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup

import versioneer

setup(version=versioneer.get_version(), cmdclass=versioneer.get_cmdclass())
