# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-06-09 16:46:54
# @Last Modified time: 2022-01-20 10:15:32
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys
import shutil
import setuptools

VERSION = '0.0.84'
PROJECT_NAME = 'pydbapi'

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('./requirements.txt', 'r', encoding='utf-8') as f:
    requires = f.readlines()

if sys.argv[1] == 'build':
    os.system('python setup.py sdist bdist_wheel')
elif sys.argv[1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system(f'python -m twine upload dist/*{VERSION}* --repository {PROJECT_NAME}')
    # shutil.rmtree(f'./{PROJECT_NAME}-{VERSION}')
    shutil.rmtree('./build')
    shutil.rmtree(f'./{PROJECT_NAME}.egg-info')
    sys.exit()

setuptools.setup(
    name=PROJECT_NAME,  # Replace with your own username
    version=VERSION,
    author="longfengpili",
    author_email="398745129@qq.com",
    description="A simple database API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://pypi.org/project/{PROJECT_NAME}/",
    packages=setuptools.find_packages(exclude=["tests.*", "tests"]),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords=["dbapi", "sqlite3", "redshift", 'snowflake'],
    python_requires=">=3.6",
    project_urls={
        'Documentation': f'https://github.com/longfengpili/{PROJECT_NAME}/blob/master/README.md',
        'Source': f'https://github.com/longfengpili/{PROJECT_NAME}',
    },
)
