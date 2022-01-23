# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phobos',
 'phobos.cli',
 'phobos.cli.cookiecutter-phobos-project.{{cookiecutter.project_name}}',
 'phobos.cli.cookiecutter-phobos-project.{{cookiecutter.project_name}}.models',
 'phobos.cli.middleware',
 'phobos.cli.utils',
 'phobos.config',
 'phobos.grain',
 'phobos.io',
 'phobos.loss',
 'phobos.metrics',
 'phobos.runner',
 'phobos.transforms']

package_data = \
{'': ['*'],
 'phobos.cli': ['cookiecutter-phobos-project/*'],
 'phobos.cli.cookiecutter-phobos-project.{{cookiecutter.project_name}}': ['.phobos_run/*']}

install_requires = \
['albumentations>=1.0.3,<2.0.0',
 'cookiecutter>=1.7.3,<2.0.0',
 'numpy>=1.21.0,<2.0.0',
 'polyaxon-sdk>=1.10.1,<2.0.0',
 'polyaxon>=1.10.1,<2.0.0',
 'pytorch-lightning>=1.3.8,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'torch>=1.10.1,<2.0.0',
 'torchvision>=0.11.2,<0.12.0',
 'webdataset==0.1.62',
 'yacs>=0.1.8,<0.2.0']

entry_points = \
{'console_scripts': ['phobos = phobos.cli:cli']}

setup_kwargs = {
    'name': 'phobos',
    'version': '1.2.3',
    'description': 'Training utility library and config manager for Granular Machine Vision research',
    'long_description': '===================\nPhobos\n===================\n\nA Utility Library that assists in Geospatial Machine Learning by: \n\n* supporting creation of a project with boilerplate code for model training\n* exporting annotations from `Europa <https://europa.granular.ai>`_\n* populating template project with configurable components for model\n* fetching samples from dataset shards available at ``AIStore``\n* orchestrating model training and validation\n* deploying project to `Arche <https://arche.granular.ai>`_ for efficient training in a node cluster   \n\nFlow\n----\n.. image:: docs/phobos.png\n    :width: 1200\n\nFeatures\n--------\n\n* Polyaxon auto-param capture\n* Configuration enforcement and management for translation into Dione environment\n* Precomposed loss functions and metrics\n* Get annotations from Europa \n\n\nTODO\n----\n\n* ETL datasets via CLI on AIStore\n* Multi Input and Multi Output models\n* Static analysis code \n* Dataset abstraction \n* Standard dataset loaders \n* Pretrained models \n\n\nBuild Details\n-------------\n\n* packages are managed using poetry\n* packages poetry maintains pyproject.toml\n* PRs and commits to `develop` branch trigger github actions\n\n\nTests\n-----\n\n>>> make install\n>>> make test-light\n\n\nA GPU machine is requried for test-heavy\n\n>>> make install\n>>> make test-heavy\n\n\nInstallation\n------------\n\n```pip install phobos```\n\n\nUsage\n-----\n\nGet all the annotation tasks available in Europa \n\n```phobos get --all --email <email> --passwd <password>```\n\nDownload one particular annotation task from Europa \n\n```phobos get --task <task ID> --path <directory to save anntoations> --email <email> --passwd <password>```\n\nCreate a project boilerplate code \n\n```phobos init --project_name <project name> --project_description <project description>```\n\nRun an experiment \n\n```phobos run```\n\nRun associated tensorboard \n\n```phobos tensorboard --uuid <project id>```\n\nLicense\n-------\nGPLv3\n\nDocumentation\n-------------\n\nView documentation `here <https://phobos.granular.ai/>`_\n\nImage\n-----\nUse gcr.io/granular-ai/phobos:latest\n',
    'author': 'Sagar Verma',
    'author_email': 'sagar@granular.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/granularai/phobos',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
