import re
from pathlib import Path
from setuptools import setup, find_packages

txt = Path('myqueue/__init__.py').read_text()
version = re.search("__version__ = '(.*)'", txt).group(1)

long_description = Path('README.rst').read_text()

setup(name='myqueue',
      version=version,
      description='Simple job queue',
      long_description=long_description,
      author='J. J. Mortensen',
      author_email='jjmo@dtu.dk',
      url='https://myqueue.readthedocs.io/',
      packages=find_packages(),
      entry_points={'console_scripts': ['mq = myqueue.cli:main']},
      install_requires=['graphlib-backport'],
      python_requires='>=3.7',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: '
          'GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: Unix',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Scientific/Engineering'])
