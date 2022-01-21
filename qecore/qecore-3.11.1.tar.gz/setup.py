#!/usr/bin/env python3
import setuptools

def scripts():
    import os
    scripts_list = os.listdir(os.curdir + "/scripts/")
    result = []
    for file in scripts_list:
        result = result + ["scripts/" + file]
    return result


setuptools.setup(
    name="qecore",
    version="3.11.1",
    author="Michal Odehnal",
    author_email="modehnal@redhat.com",
    description="DesktopQE Tool for unified test execution",
    url="https://gitlab.com/dogtail/qecore",
    packages=setuptools.find_packages(),
    scripts=scripts(),
    install_requires=[
        "behave",
        "behave-html-formatter",
        "dasbus",
        "termcolor"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    options={
        "build_scripts": {
            "executable": "/usr/bin/python3",
        }
    }
)
