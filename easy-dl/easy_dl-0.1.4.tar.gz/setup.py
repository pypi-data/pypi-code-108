import os, shutil
from setuptools import setup, find_packages

#移除构建的build文件夹
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(CUR_PATH, 'build')
if os.path.isdir(path):
    print('INFO del dir ', path) 
    shutil.rmtree(path)


setup(
    name = 'easy_dl', #应用名
    author = 'oncemonkey',
    description="A small package for deep learning that setup config and log metric based on pytorch and tensorboard",
    version = '0.1.4',  #版本号
    url="https://github.com/OnceMonkey/easy-dl",
    packages = find_packages(),  #包括在安装包内的Python包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)