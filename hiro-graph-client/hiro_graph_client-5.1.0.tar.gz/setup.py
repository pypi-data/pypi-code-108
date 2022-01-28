from os import path

from setuptools import setup, find_packages

import timestamp
import version_by_git

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as fr:
    long_description = fr.read()
with open(path.join(this_directory, '../CHANGELOG.md'), encoding='utf-8') as fc:
    long_description += "\n---\n# CHANGELOG\n---\n"
    long_description += fc.read()

subversion = timestamp.make_timestamp()

name = 'hiro_graph_client'

__version__ = version_by_git.create_version_file(name)

setup(
    name=name,
    version=__version__,
    packages=find_packages(),
    python_requires='>=3.7',

    install_requires=[
        'wheel',
        'requests',
        'backoff',
        'websocket-client',
        'apscheduler'
    ],
    package_data={
        name: ['VERSION']
    },

    project_urls={
        'GitHub': 'https://github.com/arago/hiro-client-python',
        'Documentation': 'https://github.com/arago/hiro-client-python/blob/master/src/README.md',
        'Changelog': 'https://github.com/arago/hiro-client-python/blob/master/CHANGELOG.md'
    },

    author="arago GmbH",
    author_email="info@arago.co",
    maintainer="Wolfgang Hübner",
    description="Hiro Client for Graph REST API of HIRO 7",
    keywords="arago HIRO7 API REST WebSocket",
    url="https://github.com/arago/hiro-client-python",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
