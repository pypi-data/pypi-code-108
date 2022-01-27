"""
@author: bakabaka9405
@file:setup.py
@time:2022/1/27 22:23
@file_desc:
"""

import setuptools

setuptools.setup(
    name='libmoceris',
    version='0.0.2',
    author='MOCERIS STUDIO',
    author_email='MocerisStudio@outlook.com',
    description='MOCERIS Gaming Engine',
    long_description='This is MOCERIS Gaming Engine',
    url='https://gitee.com/moceris-studio/libmoceris',
    packages=setuptools.find_packages(),
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
