# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlflow_oss']

package_data = \
{'': ['*']}

install_requires = \
['oss2>=2.15.0,<3.0.0']

entry_points = \
{'mlflow.artifact_repository': ['oss = '
                                'mlflow_oss.artifact_repo:OSSArtifactRepository']}

setup_kwargs = {
    'name': 'mlflow-oss-store',
    'version': '0.1.0',
    'description': 'MLflow artifact store plugin for AliCloud OSS',
    'long_description': None,
    'author': 'Guan Hao',
    'author_email': 'raptium@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/raptium/mlflow-oss-store.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
