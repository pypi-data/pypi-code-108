# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gwcloud_python',
 'gwcloud_python.tests',
 'gwcloud_python.utils',
 'gwcloud_python.utils.tests']

package_data = \
{'': ['*'],
 'gwcloud_python': ['.pytest_cache/*', '.pytest_cache/v/cache/*'],
 'gwcloud_python.tests': ['.pytest_cache/*', '.pytest_cache/v/cache/*'],
 'gwcloud_python.utils': ['.pytest_cache/*', '.pytest_cache/v/cache/*']}

install_requires = \
['graphene-file-upload>=1.3.0,<2.0.0',
 'gwdc-python>=0.3.0,<0.4.0',
 'importlib-metadata>=4.5.0,<5.0.0',
 'jwt>=1.2.0,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'tqdm>=4.61.2,<5.0.0']

extras_require = \
{'docs': ['Sphinx>=4.0.2,<5.0.0', 'sphinx-rtd-theme>=0.5.2,<0.6.0']}

setup_kwargs = {
    'name': 'gwcloud-python',
    'version': '1.6.0',
    'description': 'Wrapper of GWDC API, used for interacting with the GWCloud endpoints',
    'long_description': "GWCloud Python API\n==================\n\n`GWCloud <https://gwcloud.org.au/>`_ is a service used to handle both the submission of `Bilby <https://pypi.org/project/bilby/>`_ jobs to a supercomputer queue and the obtaining of the results produced by these jobs.\nWhile there is a web interface for this service, which is recommended for beginners, this package can be used to allow Bilby job submission and manipulation from Python scripts.\n\nCheck out the `documentation <https://gwcloud-python.readthedocs.io/en/latest/>`_ for more information.\n\nInstallation\n------------\n\nThe gwcloud-python package can be installed with\n\n::\n\n    pip install gwcloud-python\n\n\nExample\n-------\n\n::\n\n    >>> from gwcloud_python import GWCloud\n    >>> gwc = GWCloud(token='<user_api_token_here>')\n    >>> job = gwc.get_preferred_job_list()[0]\n    >>> job.save_corner_plot_files()\n\n    100%|██████████████████████████████████████| 3.76M/3.76M [00:00<00:00, 5.20MB/s]\n    All 2 files saved!\n",
    'author': 'Thomas Reichardt',
    'author_email': 'treichardt@swin.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gravitationalwavedc/gwcloud_python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
