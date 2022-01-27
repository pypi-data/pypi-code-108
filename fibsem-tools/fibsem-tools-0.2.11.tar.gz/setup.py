# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fibsem_tools',
 'fibsem_tools.io',
 'fibsem_tools.metadata',
 'fibsem_tools.scripts']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.10.0,<2.0.0',
 'dacite>=1.6.0,<2.0.0',
 'dask-jobqueue==0.7.3',
 'distributed>=2021.10.0',
 'fsspec==2021.07.0',
 'h5py>=3.1.0,<4.0.0',
 'mrcfile>=1.2.0,<2.0.0',
 'numpy>=1.20.0,<2.0.0',
 'pandas>=1.2.3,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 's3fs>=2021.7.0,<2022.0.0',
 'tensorstore>=0.1.8,<0.2.0',
 'xarray-multiscale>=0.3.0,<0.4.0',
 'xarray>=0.20.0,<0.21.0',
 'zarr>=2.10.3,<3.0.0']

setup_kwargs = {
    'name': 'fibsem-tools',
    'version': '0.2.11',
    'description': 'Tools for processing FIBSEM datasets',
    'long_description': None,
    'author': 'Davis Vann Bennett',
    'author_email': 'davis.v.bennett@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4',
}


setup(**setup_kwargs)
