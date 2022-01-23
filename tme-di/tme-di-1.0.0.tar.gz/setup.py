# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='tme-di',  # 项目名称,也就是pip list后会出来的包名
    version='1.0.0',
    author = 'tme-di',
    author_email="pengluan@tencent.com",
    packages=find_packages('di'),  # 包含所有的py文件
    package_dir={'': 'di'},  # 包的地址
    include_package_data=True,  # 将数据文件也打包
    zip_safe=True,
    python_requires='>=3.6',
    install_requires=[
        'pysnooper >= 11.0',
        'pika >= 1.2.0'
    ]
)



