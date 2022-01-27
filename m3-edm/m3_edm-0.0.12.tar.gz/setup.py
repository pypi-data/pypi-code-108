from setuptools import (
    find_packages,
    setup,
)

PROJECT = 'm3_edm'

VERSION = '0.0.12'


try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Electronic Document Management',
    long_description=long_description,

    author='Alexander Danilenko',
    author_email='a.danilenko@bars.group',

    url='http://docs.budg.bars.group/m3_edm/',
    download_url='',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    package_data={
        '': [],
    },

    install_requires=[
        'function-tools>=0.1.6',
    ],

    zip_safe=False,
)
