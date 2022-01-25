import re

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("tsvkit/__init__.py", encoding="utf-8") as f:
    version = re.search(r'__version__\s*=\s*"(.*)"', f.read()).group(1)

setup(
    name="tsvkit",
    license="MIT",
    version=version,
    description="TSV toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="singchen",
    author_email="xhqsm@qq.com",
    url="https://gitee.com/xhqsm/tsvkit/",
    packages=find_packages(),
    entry_points={"console_scripts": ["tsvkit=tsvkit:main"]},
)
