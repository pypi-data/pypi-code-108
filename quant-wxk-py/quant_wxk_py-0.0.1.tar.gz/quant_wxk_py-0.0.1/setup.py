import setuptools
from sqlalchemy import desc

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name = 'quant_wxk_py',
    version = '0.0.1',
    author='wxk',
    author_email='wangxk20@qq.com',
    description='A small example package',
    long_description='A small example package',
    long_description_content_type = 'text/markdown',
    url = '',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

