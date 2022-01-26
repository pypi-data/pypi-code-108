# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_point_client',
 'data_point_client.api',
 'data_point_client.api.data_export',
 'data_point_client.api.data_point',
 'data_point_client.api.files',
 'data_point_client.models',
 'data_source_client',
 'data_source_client.api',
 'data_source_client.api.data_import',
 'data_source_client.api.data_source',
 'data_source_client.api.file',
 'data_source_client.models',
 'gnista_library']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.1.0,<3.0.0',
 'attrs>=20.1.0,<22.0.0',
 'colorama>=0.4.4,<0.5.0',
 'httpx>=0.15.4,<0.19.0',
 'keyring>=23.1.0,<24.0.0',
 'oauth2-client>=1.2.1,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'structlog>=21.1.0,<22.0.0']

setup_kwargs = {
    'name': 'gnista-library',
    'version': '1.3.3',
    'description': 'A client library for accessing gnista.io',
    'long_description': '[![Gitlab Pipeline](https://gitlab.com/campfiresolutions/public/gnista.io-python-library/badges/main/pipeline.svg)](https://gitlab.com/campfiresolutions/public/gnista.io-python-library/-/pipelines)  [![Python Version](https://img.shields.io/pypi/pyversions/gnista-library)](https://pypi.org/project/gnista-library/)  [![PyPI version](https://img.shields.io/pypi/v/gnista-library)](https://pypi.org/project/gnista-library/)  [![License](https://img.shields.io/pypi/l/gnista-library)](https://pypi.org/project/gnista-library/)  [![Downloads](https://img.shields.io/pypi/dm/gnista-library)](https://pypi.org/project/gnista-library/) \n\n# gnista-library\nA client library for accessing gnista.io\n\n## Tutorial\n### Create new Poetry Project\nNavigate to a folder where you want to create your project and type\n```shell\npoetry new my-gnista-client\ncd my-gnista-client\n```\n\n### Add reference to your Project\nNavigate to the newly created project and add the PyPI package\n```shell\npoetry add gnista-library\n``` \n\n### Your first DataPoint\nCreate a new file you want to use to receive data this demo.py\n\n```python\nfrom gnista_library import KeyringGnistaConnection, GnistaDataPoint, GnistaDataPoints\n\nconnection = KeyringGnistaConnection()\n\ndata_point_id = "56c5c6ff-3f7d-4532-8fbf-a3795f7b48b8"\ndata_point = GnistaDataPoint(connection=connection, data_point_id=data_point_id)\n\ndata_point_data = data_point.get_data_point_data()\n\nprint(data_point_data)\n```\n\nYou need to replace the `DataPointId` with an ID from your gnista.io workspace.\n\nFor example the DataPointId of this DataPoint `https://aws.gnista.io/secured/dashboard/datapoint/4684d681-8728-4f59-aeb0-ac3f3c573303` is `4684d681-8728-4f59-aeb0-ac3f3c573303`\n\n### Run and Login\nRun your file in poetry\'s virtual environment\n```console\n$ poetry run python demo.py\n2021-09-02 14:51.58 [info     ] Authentication has been started. Please follow the link to authenticate with your user: [gnista_library.gnista_connetion] url=https://aws.gnista.io/authentication/connect/authorize?client_id=python&redirect_uri=http%3A%2F%2Flocalhost%3A4200%2Fhome&response_type=code&scope=data-api%20openid%20profile%20offline_access&state=myState\n```\nIn order to login copy the `url` into your Browser and Login to gnista.io or, if allowed a browser window will open by itself.\n\n### Keystore\nOnce you loggedin, the library will try to store your access token in your private keystore. Next time you run your programm, it might request a password to access your keystore again to gain access to gnista.io\nPlease take a look at [Keyring](https://pypi.org/project/keyring/) for details.\n\n## Advanced Example\n### Show received Data in a plot\n```shell\npoetry new my-gnista-client\ncd my-gnista-client\npoetry add gnista-library\npoetry add structlib\npoetry add matplotlib\n```\n\n```python\nimport matplotlib.pyplot as plt\nfrom structlog import get_logger\n\nfrom gnista_library import KeyringGnistaConnection, GnistaDataPoint, GnistaDataPoints\n\nlog = get_logger()\n\nconnection = KeyringGnistaConnection()\n\ndata_point_id = "56c5c6ff-3f7d-4532-8fbf-a3795f7b48b8"\ndata_point = GnistaDataPoint(connection=connection, data_point_id=data_point_id)\n\ndata_point_data = data_point.get_data_point_data()\nlog.info("Data has been received. Plotting")\ndata_point_data.plot()\nplt.show()\n\n```\n\n### Filter by DataPoint Names\n```shell\npoetry new my-gnista-client\ncd my-gnista-client\npoetry add gnista-library\npoetry add structlib\npoetry add matplotlib\n```\n\n```python\nimport matplotlib.pyplot as plt\nfrom structlog import get_logger\n\nfrom gnista_library import KeyringGnistaConnection, GnistaDataPoint, GnistaDataPoints\n\nlog = get_logger()\n\nconnection = KeyringGnistaConnection()\n\ndataPoints = GnistaDataPoints(connection=connection)\ndata_point_list = list(dataPoints.get_data_point_list())\n\nfor data_point in data_point_list:\n    log.info(data_point)\n\n# Find Specific Data Points\nfiltered_data_points = filter(\n    lambda data_point: data_point.name.startswith("371880214002"), data_point_list\n)\nfor data_point in filtered_data_points:\n    # get the data\n    data_point_data = data_point.get_data_point_data()\n    log.info(data_point_data)\n    data_point_data.plot()\n    plt.show()\n\n```\n\n\n\n## Links\n**Website**\n[![gnista.io](https://www.gnista.io/assets/images/gnista-logo-small.svg)](gnista.io)\n\n**PyPi**\n[![PyPi](https://pypi.org/static/images/logo-small.95de8436.svg)](https://pypi.org/project/gnista-library/)\n\n**GIT Repository**\n[![Gitlab](https://about.gitlab.com/images/icons/logos/slp-logo.svg)](https://gitlab.com/campfiresolutions/public/gnista.io-python-library)',
    'author': 'Markus Hoffmann',
    'author_email': 'markus@campfire-solutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gnista.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
