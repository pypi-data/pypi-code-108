# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbx_component_files_uploader',
 'pbx_component_files_uploader.exceptions',
 'pbx_component_files_uploader.ext.selectel',
 'pbx_component_files_uploader.interfaces']

package_data = \
{'': ['*']}

install_requires = \
['requests==2.27.1']

setup_kwargs = {
    'name': 'pbx-component-files-uploader',
    'version': '0.0.1',
    'description': 'Files uploader to custom storages',
    'long_description': "# pbx-lv2-records-uploader\n\nSimple selectel upload\n\n```python\n    api = Uploader(Uploader.SERVICE_SELECTEL, {\n        'username': 'user',\n        'password': 'pass',\n        'container': 'container_name'\n    }, {\n        'token_cache_dir': '/path/to/cache/dir'\n    })\n\n    uploadedFileUrl = api.upload(\n        '/path/to/src/file', 'dst_folder/dst_filename')\n        \n    print(uploadedFileUrl)\n```\n",
    'author': 'Ivan Kalashnikov',
    'author_email': 'ivan@leadvertex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/leadvertex/pbx-component-files-uploader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
