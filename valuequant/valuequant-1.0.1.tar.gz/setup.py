# 著作者：叶凯文
# Author: YE KAIWEN
# 版权归著作者叶凯文所有
# Copyright (c) 2022 YE KAIWEN. All Rights Reserved.

from setuptools import setup,find_packages

setup(
    name='valuequant',
    version='1.0.1',
    description='Provide timeseries modeling and stock valuation service.',
    long_description='valuequant provide timeseries modeling and stock valuation service. Register for a service account and get start on https://www.boomevolve.com',
    long_description_content_type='text/plain',
    url='https://www.boomevolve.com/valuequant',
    author='YE KAIWEN',
    author_email='kevinye@originalbooms.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords=("Quant","Data Science","Statistics","Value Analysis"),
    project_urls={
        'Documentation':'https://www.boomevolve.com/valuequant',
        'Register':'https://www.boomevolve.com/'
    },
    packages=find_packages(include=['valuequant','valuequant.*']),
    install_requires=['pandas','requests'],
    python_requires='>=3',
)
