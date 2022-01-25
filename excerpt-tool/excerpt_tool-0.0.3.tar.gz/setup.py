#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='excerpt_tool', # 项目的名称,pip3 install get-time
    version='0.0.3', # 项目版本 
    author='Mryan2005', # 项目作者 
    url='https://github.com/Mryan2005/excerpt_tool', # 项目代码仓库
    description='一个摘录软件', # 项目描述 
    packages=['excerpt_tool'], # 包名 
    install_requires=[],
    entry_points={
        'console_scripts': [
            'excerpte=excerpt_tool:main', # 使用者使用excerpt时,就睡到excerpt项目下的__init__.py下执行excerpt函
        ]
    } # 重点
)

