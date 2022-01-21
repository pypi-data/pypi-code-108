from setuptools import setup
import setuptools
from lsbatch import constants

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='lsbatch',
    version=constants.CURRENT_VERSION,
    packages=setuptools.find_packages(),
    package_data={
        'lsbatch': ['*'],
        'lsbatch.lsq_batch_template': ['*']
    },
    author="MarketXpander Services Pvt. Ltd.",
    author_email="batchjobs@leadsquared.com",
    description="lsbatch LeadSquared provided Batch Jobs software development kit. This allows developers to code and test Batch Jobs offline.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'lsbatch = lsbatch.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
