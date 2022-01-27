# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
from setuptools import setup, find_packages


setup(
    name='melon-boot',
    version='1.0.6',
    author='zh_o',
    author_email='isbo.zh@outlook.com',
    description='The ui automation framework',
    include_package_data=True,
    packages=find_packages(),
    install_requires=['toml', 'selenium', 'pytest', 'allure-pytest', 'faker']
)
