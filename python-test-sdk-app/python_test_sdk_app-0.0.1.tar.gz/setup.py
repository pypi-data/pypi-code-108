
#!/usr/bin/env python
# coding:utf-8
from setuptools import setup

setup(
    name='python_test_sdk_app', # 应用名
    version='0.0.1', # 版本号 
    description="your module", # 描述
 	 author="Example Wmm ",  # 作者
    packages=['testapp'], # 包括在安装包内的 Python 包
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ]
    # url="https://blog.csdn.net/hejp_123",
  	 # packages = find_packages()
)