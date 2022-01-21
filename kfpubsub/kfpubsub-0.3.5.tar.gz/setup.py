from setuptools import setup
from os import path

current_dir = path.abspath(path.dirname(__file__))

with open(path.join(current_dir, 'README.md')) as f:
    long_description = f.read()

setup(
      name='kfpubsub',
      version='0.3.5',
      description='Base redis pubsub implementation',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://gitlab.com/kas-factory/packages/pubsub',
      author='Antonio @ KF',
      author_email='antonio@kasfactory.net',
      license='COPYRIGHT',
      packages=['kfpubsub'],
      install_requires=[
            'redis>=3.3.8',
            'kafka-python>=2.0.2',
      ],
      zip_safe=False)
