import sys
import os
from setuptools import setup, find_packages
from cerberus_kind import __version__

def main():
    # Read Description form file
    try:
        with open('README.rst') as f:
            description = f.read()
    except:
        print('Cannot find README.md file.', file=sys.stderr)
        description = "Kind Schema Extender for Cerberus Python."

    setup(
      name='cerberus_kind',
      version=__version__,
      description='Help to select a schema by "kind" key on cerberus.',
      long_description=description,
      author='Hyoil LEE',
      author_email='onetop21@gmail.com',
      license='MIT License',
      packages=find_packages(exclude=['.temp', '.test']),
      url='https://github.com/onetop21/cerberus-kind.git',
      zip_safe=False,
      python_requires='>=3.0',
      install_requires=["Cerberus>=1.3.4,<2"],
    )

if __name__ == '__main__':
    main()