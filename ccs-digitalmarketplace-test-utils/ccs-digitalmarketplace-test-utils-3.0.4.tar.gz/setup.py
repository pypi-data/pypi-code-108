"""
Utilities for testing Digital Marketplace apps.
"""
import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('dmtestutils/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='ccs-digitalmarketplace-test-utils',
    version=version,
    url='https://github.com/Brickendon-DMp1-5/digitalmarketplace-test-utils',
    license='MIT',
    author='GDS Developers',
    description=__doc__.strip().split('\n')[0],
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    ],  # Dependency list should be minimal: if a particular test helper has a dependency on another lib (such as
        # Flask) then your app will already have that dependency included, and there's no need to add it here. If you
        # aren't using that particular function, you have no need of the dependency, so we should not install it by
        # default. Only add dependencies here if you introduce a new dependency that exists solely for testing purposes.
    python_requires="~=3.8",
    entry_points={
        'console_scripts': [
        ],
    },
)
