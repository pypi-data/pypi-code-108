"""Package specification."""
import os
from pathlib import Path
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


def get_readme():
    """
    Retrieve content of projects readme file.

    Returns:
        str: The content of README.md as a string.

    """
    readme_dir = Path(__file__).parent
    return (readme_dir / "README.md").read_text()


setup(name='verso',
      description='Verso provides functionality for managing versioning',
      url='https://github.com/tfagerlind/verso',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      license='MIT',
      maintainer='Tomas Fägerlind',
      maintainer_email='tomas.fagerlind@sofengi.com',
      version=get_version(),
      long_description=get_readme(),
      long_description_content_type='text/markdown',
      scripts=['verso'],
      packages=['core'],
      install_requires=['click', 'semver', 'gitpython'])
