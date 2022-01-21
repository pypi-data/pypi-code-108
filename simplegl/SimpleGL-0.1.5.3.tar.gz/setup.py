# -*- coding: utf-8 -*- 
# @Time : 2/20/21 3:03 PM 
# @Author : mxt
# @File : setup.py
import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SimpleGL",
    version="0.1.5.3",
    author="Maoxinteng",
    author_email="1214403402@qq.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/bbnoodle/simple_gl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    install_requires=["GITCodeAnalysis==1.0.1"]
)
