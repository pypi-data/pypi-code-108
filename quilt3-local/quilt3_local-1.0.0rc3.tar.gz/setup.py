# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quilt3_local', 'quilt3_local.lambdas', 'quilt3_local.lambdas.shared']

package_data = \
{'': ['*'], 'quilt3_local': ['catalog_bundle/*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'aicsimageio==3.0.7',
 'aiobotocore>=2.1.0,<3.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'ariadne>=0.14.0,<0.15.0',
 'boto3>=1.10.0,<2.0.0',
 'botocore>=1.23.14,<2.0.0',
 'cachetools>=5.0.0,<6.0.0',
 'fastapi>=0.70.0,<0.71.0',
 'fcsparser>=0.2.4,<0.3.0',
 'imageio==2.5.0',
 'importlib-resources>=5.3.0,<6.0.0',
 'jsonschema>=3.0.1,<4.0.0',
 'nbconvert>=6.3.0,<7.0.0',
 'nbformat>=5.1.3,<6.0.0',
 'numpy>=1.21.4,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'requests>=2.26.0,<3.0.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['quilt3-local = quilt3_local.main:run']}

setup_kwargs = {
    'name': 'quilt3-local',
    'version': '1.0.0rc3',
    'description': 'Quilt3 catalog: local development mode',
    'long_description': '# Quilt3 catalog: Local development mode\n\nOpen source implementation of the Quilt3 registry that works in the local\nenvironment (not requiring AWS cloud services aside from S3 / S3 Select).\n\nThis package is not intended to be installed/used directly by end users.\nInstead, install `quilt3[catalog]` and use `quilt3 catalog` CLI command.\n\n## Developing\n\n### TL;DR\n\n```shell\n# set up venv, assuming poetry is available in the PATH\npoetry install\n\n# build catalog bundle\n(cd ../catalog && npm i && npm run build && cp -r build ../quilt3_local/quilt3_local/catalog_bundle)\n\n# run the app at http://localhost:3000\npoetry run quilt3-local\n```\n\n### Set-up\n\n#### Python environment set-up\n\nFirst, you need [`poetry` installed](https://python-poetry.org/docs/#installation).\n\nThen, you have to set up the virtualenv by running `poetry install` from the\nproject directory -- it will create a virtualenv and install the requirements.\n\n#### Catalog (node.js) environment set-up\n\nRefer to the [catalog documentation](../catalog/).\n\n### Running\n\nYou can either serve a static catalog bundle (produced by `npm run build`) or\nproxy static files from a running catalog instance.\n\n**NOTE**: you need valid AWS credentials available, see\n[boto3 docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials) for details.\n\n#### Serving a static catalog bundle\n\nRun `poetry run quilt3-local` to start the app on port 3000 serving the static\ncatalog bundle from the `./quilt3_local/catalog_bundle` directory.\nPath to the bundle can be overriden by `QUILT_CATALOG_BUNDLE` env var.\nPort can be configured via `PORT` env var.\n\nIn order to serve the bundle, you should first build it by running\n`npm run build` from the catalog directory and then either copying it to\n`./quilt3_loca/catalog_bundle` or overriding `QUILT_CATALOG_BUNDLE` to point to\nyour bundle.\nHowever, this approach is not very convenient when developing catalog features,\nsince it requires rebuilding the bundle to pick up the changes.\nTo address this there\'s a "proxy" mode available.\n\n#### Proxying a running catalog instance\n\nIn this mode the app proxies all the static files requests to a running catalog\ninstance. One can be started by executing `PORT=3001 npm start` from the catalog\ndirectory (setting port to `3001` required to avoid conflict with the `quilt3_local`\napp\'s default settings).\n\nAfter starting up a catalog instance, you can start the `quilt3_local` app and\npoint it to that instance by running\n`QUILT_CATALOG_URL=http://localhost:3001 poetry run quilt3-local`\n(the app will be available at `http://localhost:3000` and will serve static\nfiles from the catalog running at `http://localhost:3001`, catalog URL\nconfigurable via `QUILT_CATALOG_URL` env var).\n\n### Building and publishing\n\n1. Bump package version in `pyproject.toml`\n\n2. Make sure you set up [credentials for `poetry`](https://python-poetry.org/docs/repositories/#configuring-credentials)\n\n3. Build and publish the package: `poetry publish --build`\n',
    'author': 'quiltdata',
    'author_email': 'contact@quiltdata.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://quiltdata.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
