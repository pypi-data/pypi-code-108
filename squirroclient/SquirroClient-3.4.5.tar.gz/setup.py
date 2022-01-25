"""
Build file for the SquirroClient.

To publish this on PyPI use:

    # Build and upload
    python setup.py sdist register upload
"""

from setuptools import find_packages, setup

install_requires = open("requirements.txt").read().splitlines()

setup(
    name="SquirroClient",
    # Version number also needs to be updated in squirro_client/__init__.py
    version="3.4.5",
    description="Python client for the Squirro API",
    long_description=open("README").read(),
    author="Squirro Team",
    author_email="support@squirro.com",
    url="http://dev.squirro.com/docs/tools/python/index.html",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.6",
    license="Commercial",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
