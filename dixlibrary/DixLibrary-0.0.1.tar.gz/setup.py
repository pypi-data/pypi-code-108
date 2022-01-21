from setuptools import setup, find_packages

from keyring import get_keyring
get_keyring()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'

]


setup(
    name='DixLibrary',
    version='0.0.1',
    packages=find_packages(),
    description='My first Python library',
    author='Me',
    license='MIT',
    classifiers=classifiers
)