from setuptools import setup, find_packages
from hycv import VERSION, DIARY
setup(
    name="HY_sdk",
    version=VERSION,
    author="Cuny",
    author_email="li_xiaochen2020@qq.com",
    description=DIARY,
    include_package_data=True,
    packages=find_packages()
)
