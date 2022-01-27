import os
import re
import shutil

import setuptools

version_file_path = os.path.join(os.path.dirname(__file__), 'rox', '__init__.py')
with open(version_file_path) as f:
    version_file_content = f.read()

try:
    version = re.findall(r"^__version__ = '([^']+)'\r?$", version_file_content, re.M)[0]
except IndexError:
    raise RuntimeError('Unable to determine version.')

with open('README.md', 'r') as fh:
    long_description = fh.read()

shutil.rmtree('dist', ignore_errors=True)

setuptools.setup(
    name='rox',
    version=version,
    author='Rollout.io',
    author_email='support@rollout.io',
    description='Rollout.io ROX Python SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://support.rollout.io/docs/python-api',
    packages=setuptools.find_packages(exclude=['server-demo', 'tests']),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    install_requires=['cryptography', 'futures; python_version == "2.7"', 'requests', 'six', 'sseclient-py', 'backoff', 'monotonic', 'python-dateutil'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
)
