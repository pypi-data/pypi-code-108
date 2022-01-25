import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="dslibrary",
    version="0.0.40",
    description="Data Science Framework & Abstractions",
    long_description=README,
    long_description_content_type="text/markdown",
    #url="n/a",
    #author="n/a",
    #author_email="n/a",
    license="Apache",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3"
    ],
    packages=["dslibrary"],
    include_package_data=True,
    install_requires=["jsonschema", "pyyaml", "pandas", "pexpect"],
    extras_require={
        "all": [
            "fsspec", "boto3", "s3fs", "gcsfs", "adlfs",    # file transfer to the main CSPs
            "psycopg2-binary", "PyMySQL", "sqlite3",        # a few SQL databases
            "openpyxl"                                      # r/w excel files
        ]
    }
    #entry_points={
    #    "console_scripts": [
    #        "dslibrary=dslibrary.__main__:main",
    #    ]
    #}
)