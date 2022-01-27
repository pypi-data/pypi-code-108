#!/usr/bin/env python3

from distutils.core import setup
from setuptools import find_packages

with open("./README.md", "rt") as f:
    long_description = f.read()

setup(
        name='quickspider',
        version='0.1.2.10',
        description='help you build a small spider quickly.',
        long_description="see github.",
        author='Ivory',
        author_email='1070642565@qq.com',
        url='https://github.com/tiwe0/quickspider.git',
        packages=find_packages(),
        package_dir={'quickspider': 'quickspider'},
        package_data={'quickspider': ['template/*.toml', 'custom/*/*']},
        scripts=['quickspider/bin/quickspidercommand']
        )
