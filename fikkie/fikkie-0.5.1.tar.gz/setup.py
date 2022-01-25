from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fikkie",
    version="0.5.1",
    description=(
        "The simplest tool for lightweight monitoring over SSH, compatible with all "
        "your favorite messengers."
    ),
    license="MIT",
    long_description=long_description,
    author="Joris Hartog (@nootr)",
    long_description_content_type="text/markdown",
    url="https://github.com/nootr/fikkie/",
    packages=["fikkie", "fikkie.notifiers"],
    scripts=["scripts/fikkie"],
    install_requires=[
        "celery==5.2.2",
        "PyYAML==6.0",
        "tinydb==4.5.2",
        "typing_extensions==4.0.1",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Celery",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Monitoring",
    ],
)
