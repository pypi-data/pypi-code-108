# encoding=utf-8
# @Time    : 2022/1/23 15:27
# @Author  : YangBiao
# @Email   : 19921297590@126.com
# @File    : setup.py
# @Version : 1.0
# @Python  : python 3.7.2

from setuptools import setup, find_packages

with open("README.rst", "r") as f:
  long_description = f.read()

setup(
    name='custom_time',
    version='1.0',
    packages=find_packages(),
    long_description=long_description,
    author='YangBiao',
    platforms=["all"],
    author_email='19921297590@126.com',
    url='',
    license='MIT License',
)