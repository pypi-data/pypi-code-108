
from setuptools import find_packages
from setuptools import setup
import platform
import os

setup(
    name="trtpy",
    version="1.0.17",
    author="djw.hope",
    author_email="512690069@qq.com",
    url="https://github.com/shouxieai/tensorRT_cpp",
    description="TensorRTPro python interface",
    python_requires=">=3.7",
    install_requires=["numpy", "requests", "tqdm"],
    packages=find_packages(),
    zip_safe=False,
    platforms="linux"
)
