#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/1 10:18
# @Author  : xgy
# @Site    : 
# @File    : setup.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from setuptools import setup, find_packages

# setuptools.setup()  # 也可有参调用，则会覆盖.cfg的对应条目

with open("README.md", "r", encoding="utf-8") as fr:
    long_description = fr.read()

setup(
    name="cspdataset",         # 包的名字，可随意取
    py_modules=["datatools"],   # 安装了包之后实际import的名字
    classifiers=['Development Status :: 3 - Alpha', "Programming Language :: Python :: 3"],
    version="0.4.6",
    author="xgy",
    author_email="example@163.com",
    description="tools for voc or coco",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(),

    install_requires=["requests", "cPython", "Cython", "loguru", "lxml", "numpy", "Pillow", "pycocotools", "tqdm", "opencv-python"],

    entry_points={'console_scripts': ['datatools = datatools.__main__:main',
                                      'evatools = datatools.eva.__main__:main',
                                      'submitools = datatools.submit.__main__:main',
                                      'edatools = datatools.eda.__main__:main',
                                      'augtools = datatools.aug.__main__:main',
                                      'valtools = datatools.val.__main__:main']}  # 定义终端入口点（命令行），将产生可执行文件datatools，会执行 datatools 模块的main函数
)

# if __name__ == '__main__':
#     print("start")
