import os

from setuptools import find_packages
from setuptools import setup

root_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_directory, "README.md"), "r") as f:
    long_description = f.read()

with open(os.path.join(root_directory, "VERSION"), "r") as f:
    version = f.read().strip()


setup(
    name="myst-v1alpha1",
    description="This is the official Python library for the Myst Platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    author="Myst AI, Inc.",
    author_email="support@myst.ai",  # TODO: make a support email?
    license="Apache 2.0",
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        "google-auth>=1.11.0, <2.0.0",
        "google-auth-oauthlib>=0.4.1, <1.0.0",
        "pytz>=2019.1",
        "requests>=2.21.0, <3.0.0",
        "urllib3>=1.24.3, <2.0.0",
        "tenacity>=6.0.0, <7.0.0",
    ],
    extras_require={
        "dev": [
            "coverage>=4.5.2",
            "mock>=3.0.5",
            "responses>=0.10.6, <1.0.0",
            "tox>=3.13.1, <4.0.0",
            "readme-renderer==24.0",
            "twine>=1.13.0",
            "check-manifest>=0.37",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
