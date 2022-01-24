from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
long_description = long_description.split('### Development', 1)[0]

setup(
    name="pf-dre-core",
    version="1.0.10",
    author="Dominic Hains",
    author_email="d.hains@uq.edu.au",
    description="Core library used by DRE and MMS Tools & Subsystems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=find_packages(
        exclude=("tests", "tests.*", "settings", "jci_historian")),
    install_requires=[
        'psycopg2-binary',
        'pandas',
        'pyYAML',
        'python-dotenv',
        'astral',
        'boto3==1.15.18'  #  This version is good ... for now - s3transfer requirement issue.
      ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or "
        "later (GPLv3+)",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)
