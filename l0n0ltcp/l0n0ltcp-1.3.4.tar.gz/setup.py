import setuptools
from Cython.Build import cythonize

# 读取项目的readme介绍
with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()


ext = setuptools.Extension("lkcp.core", sources=[
                           "lkcp/core.pyx", "lkcp/ikcp.c"])

lkcp = cythonize(ext)

setuptools.setup(
    name="l0n0ltcp",  # 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="1.3.4",
    author="l0n0l",  # 项目作者
    author_email="1038352856@qq.com",
    description="对asyncio tcp的一些易用性封装",  # 项目的一句话描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/l00n00l/l0n0ltcp",  # 项目地址
    packages=setuptools.find_packages(),
    ext_modules=lkcp,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pymonocypher",
        "rsa",
        "l0n0lutils>=1.0.6",
        "Cython"
    ],
    entry_points={
        "console_scripts": [
            "l0n0lsocks5 = l0n0ltcp.commands:run_socks5_server",
            "l0n0ltranssocks5 = l0n0ltcp.commands:run_tsocks5_server",
            "l0n0ltransclient = l0n0ltcp.commands:run_trans_client",
            "l0n0ltransserver = l0n0ltcp.commands:run_trans_server",
        ]
    }
)
