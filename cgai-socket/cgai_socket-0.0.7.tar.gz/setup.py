# -*- coding:utf-8 -*-
import os
import setuptools
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="cgai_socket",
    version="0.0.7",
    author="Master Zhang",
    author_email="360014296@qq.com",
    description="A simple and fast library supporting custom callback function.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zxzxde/cgai-socket",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)