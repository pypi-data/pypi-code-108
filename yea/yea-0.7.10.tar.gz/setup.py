# -*- coding: utf-8 -*-
"""yea setup."""

from setuptools import setup


setup(
    name="yea",
    version="0.7.10",
    description="Test harness breaking the sound barrier",
    packages=["yea"],
    install_requires=[
        "coverage",
        "importlib-metadata>=3.0.0",
        "jsonschema",
        "junit-xml",
        "PyYAML",
        "requests",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "yea=yea.cli:cli",
        ]
    },
    include_package_data=True,
    package_data={"": ["yea/schema-*.json"]},
    zip_safe=False,
    license="MIT license",
    python_requires=">=3.6",
)
