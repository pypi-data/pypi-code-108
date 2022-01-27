import os
import logging

from importlib.machinery import SourceFileLoader
from setuptools import setup, find_packages

version = (
    SourceFileLoader("databricks_registry_webhooks.version", os.path.join("databricks_registry_webhooks", "version.py")).load_module().VERSION
)

setup(
    name="databricks-registry-webhooks",
    version=version,
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "databricks-cli>=0.8.7",
        "protobuf>=3.7.0",
        "packaging",
    ],
    zip_safe=False,
    author="Databricks",
    description="Databricks MLflow Model Registry Webhooks Client",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    classifiers=["Intended Audience :: Developers", "Programming Language :: Python :: 3.7"],
    keywords="ml ai databricks mlops mlflow model registry webhooks triggers cicd events",
    url="https://docs.databricks.com/applications/mlflow/model-registry-webhooks.html",
    python_requires=">=3.7",
    project_urls={
        "Documentation": "https://docs.databricks.com/applications/mlflow/model-registry-webhooks.html",
    }
)
