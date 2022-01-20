# Author: Tomohiro Kioka <p9u78sxh@s.okayama-u.ac.jp>
# Copyright (c) 2022 Tomohiro Kioka

from setuptools import setup
import pyabelab

DESCRIPTION = "Library that are likely to be used frequently in ABELAB."
NAME = 'pyabelab'
AUTHOR = 'Tomohiro Kioka'
AUTHOR_EMAIL = 'p9u78sxh@s.okayama-u.ac.jp'
URL = ''
LICENSE = 'MIT'
DOWNLOAD_URL = ''
VERSION = pyabelab.__version__
PYTHON_REQUIRES = ">=3.6"

# 必須パッケージ
INSTALL_REQUIRES = [
    'numpy >=1.19.2',
]

# 推薦パッケージ
EXTRAS_REQUIRE = {
    'tutorial': [
        'mlxtend>=0.18.0',
        'xgboost>=1.4.2',
    ]
}

PACKAGES = [
    'pyabelab'
]

CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3 :: Only',
]

with open('README.md', 'r') as fp:
    readme = fp.read()
long_description = readme

setup(name=NAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=AUTHOR,
      maintainer_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=long_description,
      license=LICENSE,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      python_requires=PYTHON_REQUIRES,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      packages=PACKAGES,
      classifiers=CLASSIFIERS
    )