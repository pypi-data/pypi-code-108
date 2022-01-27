import os
from setuptools import setup

setup(
    name='lintest',
    version='1.5.6',
    author='Wang Lin',
    author_email='think_wl@163.com',
    packages=['lintest'],
    install_requires=[
    	"psutil",
    	"requests",
    	"selenium",
    	"selenium-wire",
    	"setuptools",
    	"urllib3",
    	"PyMySQL",
    	"chromedriver_autoinstaller"
    ],
)

# python setup.py sdist --formats=gztar,zip
