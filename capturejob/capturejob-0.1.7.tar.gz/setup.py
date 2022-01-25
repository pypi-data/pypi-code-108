# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['capturejob', 'capturejob.service']

package_data = \
{'': ['*']}

install_requires = \
['azure-storage-blob>=12.9.0,<13.0.0',
 'dotmap>=1.3.26,<2.0.0',
 'dyndebug>=0.2.0,<0.3.0',
 'loguru>=0.5.3,<0.6.0',
 'python-dotenv>=0.19.2,<0.20.0']

entry_points = \
{'console_scripts': ['start = capturejob.main:main', 'test = pytest:main']}

setup_kwargs = {
    'name': 'capturejob',
    'version': '0.1.7',
    'description': 'A library to capture job outputs to persistent storage',
    'long_description': '# CaptureJob\n\nThis library provides the ability to copy stdout and stderr files to cloud storage.\n\n## Usage\n\nProgrammatically it is used like this:\n```\nfrom capturejob import CaptureJob\n\nCaptureJob()\n```\n\nbut mainly its intended to be used in a dockerfile command script followng execution of a command script.\n\n```\necho "Running batch"\n\ncd /work && poetry run python src/etl_noop/batchrun.py\n\nJOB="...\nCAPTURE_CONNECTION_STRING="..." \nCAPTURE_CONTAINER_NAME="..."\npoetry run python -m capturejob \n\necho "Done"\n```\n\n## Configuration\n\nThe following environment variables need to be set\n\n- JOB:  A name of the job which is used in the storage folder name created\n- CAPTURE_CONNECTION_STRING: Azure connection string\n- CAPTURE_CONTAINER_NAME: Azure container name\n',
    'author': 'aurecon',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
