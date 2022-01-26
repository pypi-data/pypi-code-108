# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biolib',
 'biolib.app',
 'biolib.biolib_api_client',
 'biolib.biolib_binary_format',
 'biolib.biolib_docker_client',
 'biolib.compute_node',
 'biolib.compute_node.cloud_utils',
 'biolib.compute_node.enclave',
 'biolib.compute_node.job_worker',
 'biolib.compute_node.job_worker.executors',
 'biolib.compute_node.job_worker.executors.remote',
 'biolib.compute_node.job_worker.executors.tars',
 'biolib.compute_node.webserver',
 'biolib.pyppeteer.docs',
 'biolib.pyppeteer.pyppeteer',
 'biolib.pyppeteer.pyppeteer.connection',
 'biolib.pyppeteer.pyppeteer.frame',
 'biolib.pyppeteer.pyppeteer.models',
 'biolib.pyppeteer.utils',
 'biolib.templates',
 'biolib.validators']

package_data = \
{'': ['*'],
 'biolib': ['biolib-js/*', 'pyppeteer/*', 'pyppeteer/.circleci/*'],
 'biolib.pyppeteer.docs': ['_static/*', '_templates/*']}

install_requires = \
['aenum>=2.2.3,<3.0.0',
 'appdirs>=1.4.3,<2.0.0',
 'cbor2==5.2.0',
 'certifi>=2019.11.28',
 'cose==0.9.dev2',
 'cryptography>=3.1',
 'docker==4.4.1',
 'flask-cors==3.0.10',
 'flask==2.0.1',
 'gunicorn==20.1.0',
 'importlib-metadata>=1.6.1',
 'nest_asyncio>=1.4.0,<1.5.2',
 'ordered_set>=4.0.1,<5.0.0',
 'pyOpenSSL==19.1.0',
 'pycryptodome==3.9.9',
 'pyee>=7.0.1,<8.0.0',
 'pyyaml>=5.3.1',
 'requests>=2.25.1',
 'termcolor==1.1.0',
 'tqdm>=4.42.1,<5.0.0',
 'websockets>=8.0']

extras_require = \
{':python_version < "3.8"': ['typing_extensions==3.10.0',
                             'typing_inspect>=0.5.0,<0.6.0']}

entry_points = \
{'console_scripts': ['biolib = biolib:call_cli']}

setup_kwargs = {
    'name': 'pybiolib',
    'version': '0.2.1239',
    'description': 'BioLib Python Client',
    'long_description': "# PyBioLib\n\nPyBioLib is a Python package for running BioLib applications from Python scripts, and the command line.\n\n### Python Example\n```python\n# pip3 install -U pybiolib\nimport biolib\nsamtools = biolib.load('samtools/samtools')\nprint(samtools.cli(args='--help'))\n```\n\n### Command Line Example\n```bash\npip3 install -U pybiolib\nbiolib run samtools/samtools --help\n```\n",
    'author': 'biolib',
    'author_email': 'hello@biolib.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/biolib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
