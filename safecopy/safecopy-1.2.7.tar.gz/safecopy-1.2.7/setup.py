'''
    Set up for safecopy

    Copyright 2018-2021 DeNova
    Last modified: 2022-01-25
'''

import os.path
import setuptools

# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="safecopy",
    version="1.2.7",
    author="denova.com",
    author_email="support@denova.com",
    maintainer="denova.com",
    maintainer_email="support@denova.com",
    description="Simple secure file copy. Alternative to rsync.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="rsync file-copy",
    license="GNU General Public License v3 (GPLv3)",
    url="https://denova.com/open/safecopy/",
    download_url="https://github.com/denova-com/safecopy/",
    project_urls={
        "Documentation": "https://denova.com/open/safecopy/",
        "Source Code": "https://github.com/denova-com/safecopy/",
    },
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop ",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: System :: Filesystems",
         ],
    py_modules=["safecopy"],
    scripts=['bin/safecopy'],
    entry_points={
    },
    setup_requires=['setuptools-markdown'],
    install_requires=['safelog', 'denova', 'pyrsync2'],
    python_requires=">=3.5",
)
