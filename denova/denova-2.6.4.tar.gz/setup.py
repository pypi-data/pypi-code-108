'''
    Set up for denova open source libraries.

    Copyright 2018-2020 DeNova
    Last modified: 2022-01-25
'''

import os.path
import setuptools

# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="denova",
    version="2.6.4",
    author="denova.com",
    author_email="support@denova.com",
    maintainer="denova.com",
    maintainer_email="support@denova.com",
    description="Open source python and django enhancements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="locks logs log-parser openssl",
    license="GNU General Public License v3 (GPLv3)",
    url="https://denova.com/open/denova_package/",
    download_url="https://github.com/denova-com/denova/",
    project_urls={
        "Documentation": "https://denova.com/open/denova_package/",
        "Source Code": "https://github.com/denova-com/denova/",
    },
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
         ],
    entry_points={
    },
    setup_requires=['setuptools-markdown'],
    install_requires=[],
    python_requires=">=3.5",
)
