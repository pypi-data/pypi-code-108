import re
from setuptools import setup, find_packages

# regex returns [('version', '0.1.1')] which is then converted to {'version': '0.1.1'}
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", open('cnvrgv2/_version.py').read()))
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='cnvrgv2',
    version=metadata["version"],
    author="Cnvrg",
    author_email="support@cnvrg.io",
    description="Python SDK library for using cnvrg",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        required
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock'
        ],
        'azure': [
            'azure-core==1.10.0',
            'azure-storage-blob==12.6.0'
        ],
        'google': [
            'google-api-core==1.23.0',
            'google-cloud-core==1.4.4',
            'google-cloud-storage==1.32.0',
            'google-auth==1.23.0',
            'google-crc32c==1.0.0',
            'google-resumable-media==1.1.0',
            'googleapis-common-protos==1.52.0'
        ]
    },
    entry_points='''
        [console_scripts]
        cnvrgv2=cnvrgv2.cli.cli:safe_entry_point
    ''',
)
