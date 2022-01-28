#!/usr/bin/env python

"""The setup script."""

from jp_birthday import __version__
from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "jeraconv",
    "jaconv",
    "Click>=7.0",
]

test_requirements = []

setup(
    author="shimakaze-git",
    author_email="shimakaze.soft+github@googlemail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 5 - Production/Stable",
        # "Natural Language :: English",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
    ],
    description="Django model for Japanese birthday.",
    entry_points={
        "console_scripts": [
            "django_jp_birthday=jp_birthday.cli:main",
            # "django_jp_birthday=django_jp_birthday.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="django_jp_birthday django birthday era",
    name="django_jp_birthday",
    packages=find_packages(
        include=[
            "jp_birthday",
            # "django_jp_birthday",
            # "django_jp_birthday.*"
        ]
    ),
    # test_suite="tests",
    # tests_require=test_requirements,
    url="https://github.com/shimakaze-git/django-jp-birthday",
    version=__version__,
    zip_safe=False,
)
