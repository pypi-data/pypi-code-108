# encoding=utf-8

from itertools import chain
from os import path

from setuptools import find_packages, setup


# read version number from file
here = path.dirname(__file__)
with open(path.join(here, 'hansken', 'VERSION')) as version:
    version_string = version.read().strip()

with open(path.join(here, 'README.md')) as readme:
    long_description = readme.read()

dependencies = ['decorator',
                'ijson>=3.1',
                'iso8601',
                'logbook>=1.0',
                'more-itertools',
                'python-dateutil',
                'requests>=2.7.0',
                'tabulate']

extras = {
    'mount': ['fusepy'],
    'kerberos': ['requests-kerberos'],
    'report': ['jinja2', 'weasyprint'],
    'shell': ['ipython'],
}

# add an additional 'extra' to encompass every optional feature
extras['all'] = list(chain.from_iterable(extras.values()))

setup(
    name='hansken',
    version=version_string,
    author='Netherlands Forensic Institute',
    author_email='hansken-support@nfi.nl',
    description='Python API to the Hansken REST endpoint',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ),

    packages=find_packages(),
    include_package_data=True,
    install_requires=dependencies,
    extras_require=extras,
    entry_points={
        'console_scripts': ['hansken=hansken.tool:run']
    }
)
