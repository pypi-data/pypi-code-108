import os
import re
from setuptools import setup

setup(name='seqence-server-demo',
      version='0.0.1',
      description='seqence-server-demo',
      author="Neeky",
      author_email="neeky@live.com",
      maintainer='Neeky',
      maintainer_email='neeky@live.com',
      scripts=['bin/sequence-client','bin/sequence-server'],
      packages=['pbes'],
      url='https://github.com/Neeky/protobuf-es',
      install_requires=['grpcio==1.39.0','grpcio-tools==1.38.1','protobuf==3.19.3'],
      python_requires='>=3.8.*',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8']
      )