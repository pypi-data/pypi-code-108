# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from qrunner import __version__, __description__

try:
    long_description = open(os.path.join('qrunner', "README.md"), encoding='utf-8').read()
except IOError:
    long_description = ""

setup(
    name="qrunner",
    version=__version__,
    description=__description__,
    author="杨康",
    author_email="772840356@qq.com",
    url="https://github.com/bluepang/qrunner",
    platforms="Android,IOS,Web",
    packages=find_packages(),
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
    package_data={
        r'': ['*.ini'],
    },
    install_requires=[
        'tidevice==0.6.1',
        'facebook-wda==1.4.6',
        'uiautomator2==2.16.13',
        'selenium==4.1.0',
        'pytest==6.2.5',
        'pytest-html== 3.1.1',
        'pytest-rerunfailures==10.2',
        'allure-pytest==2.9.45',
        'pytest-dependency==0.5.1',
        'pandas==1.3.4',
        'openpyxl==3.0.9',
        'XlsxWriter==3.0.2',
        'jira==3.1.1',
        'pytest-xdist==2.5.0',
        'webdriver-manager==3.5.2'
    ],
    entry_points={
        'console_scripts': [
            'qrun = qrunner.cli:main',
            'qrunner = qrunner.cli:main'
        ]
    },
)
