"""Package specification."""
import os
from setuptools import setup


def get_version():
    """
    Get version from context .

    Retrieves version from the environment variable VERSION.

    Raise:
        Exception: Raised if environment variable VERSION is not set.

    """
    if 'VERSION' not in os.environ:
        raise Exception("Environment variable VERSION must be set!")

    return os.environ['VERSION']


setup(name='verso',
      description='Verso provides functionality for managing versioning',
      url='https://github.com/tfagerlind/verso',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      maintainer='Tomas Fägerlind',
      maintainer_email='tomas.fagerlind@sofengi.com',
      version=get_version(),
      scripts=['verso'],
      packages=['core'],
      install_requires=['click', 'semver', 'gitpython'])
