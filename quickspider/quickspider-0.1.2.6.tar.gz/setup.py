#!/usr/bin/env python3

from distutils.core import setup

with open("./README.md", "rt") as f:
    long_description = f.read()

setup(
        name='quickspider',
        version='0.1.2.6',
        description='help you build a small spider quickly.',
        long_description="see github.",
        author='Ivory',
        author_email='1070642565@qq.com',
        url='https://github.com/tiwe0/quickspider.git',
        packages=['quickspider', 'quickspider.core', 'quickspider.template',
            'quickspider.test'],
        package_dir={'quickspider': 'quickspider'},
        package_data={'quickspider': ['template/*.toml']},
        scripts=['quickspider/bin/quickspidercommand']
        )
