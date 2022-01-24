import site
import sys
from setuptools import setup
from setuptools import find_packages
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]


with open("./README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


with open("./requirements.txt") as f:
    install_requires = f.read().splitlines()


setup(
    name='rally-cli',
    version='0.1.5',
    packages=find_packages(
        where='.',
        exclude=['tests']
    ),
    url='',
    license='MIT',
    author='juguerre',
    author_email='juguerre@gmail.com',
    description='Rally Software API Client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires
)
