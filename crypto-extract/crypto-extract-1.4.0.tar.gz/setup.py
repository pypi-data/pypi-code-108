import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read('README.md') if os.path.isfile("README.md") else ""

setup(
    name='crypto-extract',
    version='1.4.0',
    author='songv',
    author_email='songwei@iftech.io',
    description='Tools for exporting Ethereum blockchain data to Redshift',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tellery/crypto-extract',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    keywords='ethereum',
    python_requires='>=3.6,<4',
    install_requires=[
        'redshift_connector==2.0.902',
        'boto3==1.20.32',
        'lxml==4.7.1',
        'click==7.1.2'
    ],
    entry_points={
        'console_scripts': [
            'ethereum-extract=ethereum.cli:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/tellery/crypto-extract/issues',
        'Source': 'https://github.com/tellery/crypto-extract',
    },
)
