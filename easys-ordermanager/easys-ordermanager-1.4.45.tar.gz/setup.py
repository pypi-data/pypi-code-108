# -*- coding: UTF-8 -*-
import os
from setuptools import setup, find_packages

import easys_ordermanager


def long_description():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
    except IOError:
        return ''


def changelog():
    try:
        return open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.md')).read()
    except IOError:
        return ''


setup(
    name=easys_ordermanager.__title__,
    packages=find_packages(),
    version=easys_ordermanager.__version__,
    description=easys_ordermanager.__description__,
    author=easys_ordermanager.__author__,
    author_email=easys_ordermanager.__author_email__,
    long_description=long_description() + '\n\n' + changelog(),
    long_description_content_type='text/markdown',
    install_requires=[
        'django>=2.2,<4.0',
        'django-countries>=6.0,<8.0',
        'django-internationalflavor>=0.4.0,<0.5.0',
        'django-model-utils>=3.1.2,<5.0.0',
        'django-phonenumber-field>=3.0.1,<7.0',
        'djangorestframework>=3.10,<3.13',
        'phonenumbers>=7.0.6,<8.13.0',
    ],
    license=easys_ordermanager.__license__,
    url=easys_ordermanager.__url__,
    download_url='',
    keywords=[],
    include_package_data=True,
    classifiers=[],
)
