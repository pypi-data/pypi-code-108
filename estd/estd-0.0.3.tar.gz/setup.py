from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="estd",
    license="MIT",
    version="0.0.3",
    description="Extended standard library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="singchen",
    author_email="xhqsm@qq.com",
    url="https://gitee.com/xhqsm/estd/",
    packages=find_packages(),
)
