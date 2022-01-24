import sys
import os
from setuptools import setup, find_packages
from cerberus_document_editor import __version__

def main():
    # Read Description form file
    try:
        with open('README.rst') as f:
            description = f.read()
    except:
        print('Cannot find README.md file.', file=sys.stderr)
        description = "Document Editor for Cerberus Schema."

    setup(
      name='cerberus_document_editor',
      version=__version__,
      description='Document Editor for Cerberus Schema.',
      long_description=description,
      author='Hyoil LEE',
      author_email='onetop21@gmail.com',
      license='MIT License',
      packages=find_packages(exclude=['.temp', '.test']),
      url='https://github.com/onetop21/cerberus-document-editor.git',
      zip_safe=False,
      python_requires='>=3.0',
      install_requires=[
          "cerberus-kind>=0.0.12,<1.0.0",
          "PyYAML>=5.4.1,<6.0.0",
          "urwid>=2.1.2,<3.0.0",
          "InterruptHandler>=0.0.4,<1.0.0"
      ],
      entry_points='''
        [console_scripts]
        cerberus-document-editor=cerberus_document_editor.__main__:main
        cde=cerberus_document_editor.__main__:main
      '''
    )

if __name__ == '__main__':
    main()
