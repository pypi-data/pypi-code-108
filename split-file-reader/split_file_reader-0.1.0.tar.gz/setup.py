import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="split_file_reader",
    version="0.1.0",
    author="Xavier Halloran",
    author_email="sfr@reivax.us",
    description="A package to read parted files on disk.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Reivax/split_file_reader",
    packages=[
        "split_file_reader",
        "split_file_reader/split_file_reader",
        "split_file_reader/split_file_writer",
        "split_file_reader/http_file_reader",
    ],
    entry_points={
        "console_scripts": [
            "split_file_reader = split_file_reader.split_file_reader.__main__:main"
        ]
    },
    # zipfile =< 3.6 may cause some tests to fail.  zipfile>=3.7 supports file-like access of the payload files,
    # which is required for some tests.
    # "Programming Language :: Python :: 3.5",
    # "Programming Language :: Python :: 3.6",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.5",
    platforms=["any"],
    extras_require={
        "network": [
            "requests",
        ]
    },
    tests_require=["pytest"],
    project_urls={
        "Source": "https://gitlab.com/Reivax/split_file_reader",
    },
    zip_safe=True,
)
