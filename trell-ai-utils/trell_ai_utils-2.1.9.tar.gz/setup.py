"""Setup for the Trell_ai_utils package."""

import setuptools
import os

"""
if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']
"""

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    author="Abhay Kumar",
    author_email="abhay@trell.in",
    name='trell_ai_utils',
    description='Trell Database connectors, slack alerter and loggers',
    #version=version,
    version="2.1.9",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/trell/trell-ai-util',
    packages=setuptools.find_packages(),
    python_requires=">=3.6.9",
    install_requires=['requests', 'emoji', 'json-utils', 'python-dotenv', 'pandas_gbq', 'google-cloud',
                      'mysql-connector', 'mysql-replication', 'subprocess32', 'psutil',
                      'SQLAlchemy', 'SQLAlchemy-JSONField', 'SQLAlchemy-Utils', 'boto', 'boto3', 'joblib',
                      'pymongo==3.10.0', 'google-cloud-bigquery==2.1.0', 'tqdm==4.49.0'],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
)
