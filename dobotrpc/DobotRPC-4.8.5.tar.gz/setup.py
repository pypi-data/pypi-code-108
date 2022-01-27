import os
from setuptools import setup, find_packages  # 这个包没有的可以pip一下

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    DESCRIPTION = f.read()

setup(
    name="DobotRPC",  # 这里是pip项目发布的名称
    version="4.8.5",  # 版本号，数值大的会优先被pip
    keywords=[
        "websocket", "JSON-RPC", "asyncio", "Dobot", "Dobotlink", "Client",
        "Server"
    ],
    description="Dobotlink communication module",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    license="Apache Licence",
    author="songlijun",
    author_email="songlijun@dobot.cc",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        "websockets==8.1", "asyncio==3.4.3", "colorlog==4.0.2",
        "demjson==2.2.4"
    ])
