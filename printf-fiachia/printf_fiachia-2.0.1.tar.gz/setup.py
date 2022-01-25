from setuptools import setup, find_packages
import os

setup(
    name="printf_fiachia",
    version="2.0.1",
    description="Easy print() with color",
    long_description=open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'README.rst'), encoding="utf8").read(),
    author="fiachia",
    author_email='208473302@qq.com',
    maintainer='fiachia',
    maintainer_email='208473302@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='',
    include_package_data=True,
    install_requires=[
    ]
)
