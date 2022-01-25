# -*- coding: utf-8 -*-
# @Time     : 2021/6/1 10:23
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : setup.py
# @Version  : Python 3.8.5 +

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as rq:
    rqm = rq.read().strip()

reqs = rqm.split('\n')

reqs_list = [k.split('==')[0] for k in reqs]

setuptools.setup(
    name="sencyber-tools",
    version="0.2.3",
    author="shigure_hotaru",
    author_email="lrscct@gmail.com",
    description="Sencyber Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ag-elf/sencyber-tools",
    project_urls={
        "Bug Tracker": "https://github.com/Ag-elf/sencyber-tools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=reqs_list,
    python_requires=">=3.8",
)
