# Author: TAKAHASHI Taro <takahashi.taro@takedasystem.com>
# Copyright (c) 2022- TAKAHASHI Taro
# Licence: MIT

from setuptools import setup

DESCRIPTION = 'imap2dict: Receiving and deleting email on an IMAP4 server.'
NAME = 'imap2dict'
AUTHOR = 'TAKAHASHI Taro'
AUTHOR_EMAIL = 'takahashi.taro@takedasystem.com'
URL = 'https://github.com/sikkimtemi/imap2dict'
LICENSE = 'MIT'
DOWNLOAD_URL = URL
VERSION = '0.1.0'
PYTHON_REQUIRES = '>=3.6'
INSTALL_REQUIRES = [
    'pytz>=2020.1'
]
PACKAGES = [
    'imap2dict'
]
KEYWORDS = 'imap imap4 json'
CLASSIFIERS=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6'
]
with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()
LONG_DESCRIPTION = readme
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url=URL,
    download_url=URL,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    keywords=KEYWORDS,
    install_requires=INSTALL_REQUIRES
)