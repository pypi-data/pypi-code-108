import setuptools
from pathlib import Path

setuptools.setup(
    name="naylepdf", #依赖包名称
    version=1.0,# 版本
    long_description=Path("README.md").read_text(), #描述
    packages=setuptools.find_packages(exclude=["tests","data"])


)
# python setup.py sdist(代码分发) bdist_wheel(内置分配)