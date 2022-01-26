from setuptools import setup, find_packages

from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="unipipeline",
    version="1.6.0",
    description="simple way to build the declarative and distributed data pipelines with python. it supports rabbitmq or kafka as a broker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aliaksandr-master/unipipeline",
    author="Aliaksandr Master",
    author_email="alxe.master@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            'unipipeline=unipipeline.main:main',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jinja2>=3.0.3",
        "amqp>=5.0.6",
        "pyyaml>=5.4.12",
        "types-pyyaml>=5.4.12",
        "pydantic>=1.8.2",
        "psycopg2-binary>=2.9.2",
        "pika>=1.2.0",
        "crontab>=0.23.0",
        "kafka-python>=2.0.2",
    ],
)
