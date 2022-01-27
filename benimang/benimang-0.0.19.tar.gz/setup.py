version = "0.0.19"
install_requires = [
    "aiohttp",
    "aiofiles",
    "python-dateutil",
    "twine",         # pip 上传包
    "pyinstaller",
    "openpyxl",
    "pytest",
    "pytest-asyncio",
    "pyecharts",     # 在python 3.10.0版本会报错需要改动 from collections.abc import Iterable
    "chardet",
    "playwright",    # playwright install chromium 需要执行安装浏览器
    "ipython",
    "nest-asyncio",  # ipython报错This event loop is already running；可以使用 nest_asyncio.apply() 解决
    "autopep8",
    "pyperclip",     # copy / paste
    "colorama",      # windows打印带颜色
    "typer",         # fastapi 命令行版本的 fastapi
    "tzdata",        # zoneinfo在windows下需要这个库的支持
    "portalocker",   # 文件锁
    "qrcode",
    "mkdocs",
    "mkdocs-material",  
]

from setuptools import setup, find_packages

setup(
    name = "benimang",
    version = version,
    keywords="beni",
    description = "utils library for Beni",
    license = "MIT License",
    url = "https://pytask.com",
    author = "Beni",
    author_email = "benimang@126.com",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = install_requires,
    entry_points={
        "console_scripts": ["beni=beni.cmd:main"],
    },
)