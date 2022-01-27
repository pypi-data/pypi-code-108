# -*- encoding: utf-8 -*-
'''
Description:  PyPI     
@created   : 2021/09/08 09:33:59
'''

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="raser",
    version="3.1.0",
    author="Xin Shi",
    author_email="Xin.Shi@outlook.com",
    description="SiC Detector Simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dt-np/raser",
    project_urls={
        "Bug Tracker": "https://github.com/dt-np/raser/issues",
        "Documentation": "http://xteam.ihep.ac.cn/research/rd50/raser/",
    }, 
    packages=find_packages(),
    license='MIT',
    classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
    ]
	)

