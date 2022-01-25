# Copyright IBM Corp. 2020. All Rights Reserved.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ibm-watson-studio-pipelines",
    version="0.2.2",
    author="Michalina Kotwica",
    author_email="michalina.kotwica@ibm.com",
    description="Python utilities for IBM Watson Studio Pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.ibm.com/AILifecycle/ibm-watson-studio-pipelines",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires = [
        'ibm_cloud_sdk_core>=3.11.3',
        'ibm-cos-sdk>=2.10.0',
        'attrs>=21.2.0',
        'requests>=2.25.1',
        'responses>=0.13.4',
        'pytest>=6.2.5',
    ],
    include_package_data=True,
)
