import io
import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


with io.open('README.md', encoding='utf-8') as fp:
    description = fp.read()
setup(name='alphad3m',
      version='0.0',
      description="AlphaD3M: NYU's AutoML System",
      long_description=description,
      long_description_content_type='text/markdown',
      author="Remi Rampin, Roque Lopez, Raoni Lourenco",
      author_email='remi.rampin@nyu.edu, rlopez@nyu.edu, raoni@nyu.edu',
      maintainer="Remi Rampin, Roque Lopez, Raoni Lourenco",
      maintainer_email='remi.rampin@nyu.edu, rlopez@nyu.edu, raoni@nyu.edu',
      license='Apache-2.0',
      classifiers=[
      ])
