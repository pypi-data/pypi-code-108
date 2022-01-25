#!/usr/bin/env python

from setuptools import setup, find_packages
import databricks.sql


with open('README.md') as readme:
    long_description = readme.read()

setup(
    name="databricks-sql-connector",
    version=databricks.sql.__version__,
    description="Databricks SQL Connector for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://databricks.com',
    author="Databricks",
    author_email="feedback@databricks.com",
    license='http://www.apache.org/licenses/LICENSE-2.0',
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
    ],
    install_requires=[
        'future',
        'thrift>=0.13.0',
    ],
    include_package_data=True,
    package_data={"databricks.sql": ["HISTORY"]}
)
