import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="django-pg-trunk",
    version="0.1.3",
    packages=find_packages(exclude=["test*"]),
    include_package_data=True,
    install_requires=[
        "Django>=2.2",
        "psycopg2-binary<2.9"
    ],
    license="Apache-2.0",
    description="A PostgreSQL profiler for Django that uses pg_stat_statements extension",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Hipo",
    author_email="faruk@hipo.biz",
    url="https://github.com/Hipo/django-pg-trunk",
    python_requires=">=3.7",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
