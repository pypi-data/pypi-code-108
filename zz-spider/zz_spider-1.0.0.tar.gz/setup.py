# -*- coding: utf-8 -*-
# @Time    : 10/14/21 6:55 PM
# @Author  : ZZK
# @File : setup.py
# @describe ：
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='zz_spider',
    version='1.0.0',
    author='zzk',
    author_email='zzk_python@163.com',
    description='python使用MQ的场景',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/qpzzk/zz_spider',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        "requests>=2.22.0",
        "pika>=1.2.0",
        "retrying>=1.3.3",
        "environs==9.4.0",
        "confluent-kafka==1.8.2",
        "kafka==1.3.5",
        "kafka-python==2.0.2",
        "pykafka==2.8.0",
        "loguru==0.5.3",
    ],
)
