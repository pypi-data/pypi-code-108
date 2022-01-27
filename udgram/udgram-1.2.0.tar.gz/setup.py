from setuptools import setup, find_packages

setup(name='udgram',
      version='1.2.0',
      description='Compute probabilities in N-grams model for tags in UD format',
      long_description=open('README_pip.txt').read(),
      author='Wellington Silva',
      author_email='wellington.71219@gmail.com',
      license='MIT',
      packages=find_packages(),
     )