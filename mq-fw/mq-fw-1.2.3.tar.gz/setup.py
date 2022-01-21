# -*- coding: UTF-8 -*-
# @Time : 2021/12/6 上午11:33 
# @Author : 刘洪波
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mq-fw',
    version='1.2.3',
    packages=setuptools.find_packages(),
    url='https://gitee.com/maxbanana',
    license='Apache',
    author='hongbo liu',
    author_email='782027465@qq.com',
    description='A message queue framework, including pulsar and rabbitmq',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['pulsar-client', 'pika'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)