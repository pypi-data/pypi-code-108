import os
from io import open
import subprocess
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open(os.path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    INSTALL_REQUIRES = f.read().split('\n')

PACKAGE_VERSION = subprocess.check_output('git describe --tags', shell=True).decode('ascii').strip()


sha = 'Unknown'
try:
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=HERE).decode('ascii').strip()
except Exception:
    pass

PACKAGE_VERSION_LOCAL = PACKAGE_VERSION + '+' + sha[:7]

setup(
  name='aitool',
  version=PACKAGE_VERSION,
  author='xiangyuejia',
  author_email='xiangyuejia@qq.com',
  description='Summarize the algorithms and data of nlp',
  long_description=LONG_DESCRIPTION,
  long_description_content_type='text/markdown',
  url='https://github.com/deepgameai/aitool.git',
  packages=find_packages(),
  classifiers=[
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
  ],
  install_requires=[] + INSTALL_REQUIRES,
  python_requires='>=3.6, <4',
)
