import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='mongodf',
    url="https://github.com/VK/mongodf",
    version=os.getenv('PYLIB_VERSION', '0.0.0'),
    packages=find_packages(),
    license="MIT",
    keywords="mongoDB pandas dataframe filter",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[
        'pymongo',
        'pandas'
    ]
)
