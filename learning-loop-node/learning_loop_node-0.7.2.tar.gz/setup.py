# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['learning_loop_node',
 'learning_loop_node.annotation_node',
 'learning_loop_node.annotation_node.tests',
 'learning_loop_node.converter',
 'learning_loop_node.converter.tests',
 'learning_loop_node.data_classes',
 'learning_loop_node.detector',
 'learning_loop_node.detector.rest',
 'learning_loop_node.detector.tests',
 'learning_loop_node.inbox_filter',
 'learning_loop_node.inbox_filter.tests',
 'learning_loop_node.rest',
 'learning_loop_node.tests',
 'learning_loop_node.trainer',
 'learning_loop_node.trainer.tests']

package_data = \
{'': ['*'],
 'learning_loop_node': ['.vscode/*'],
 'learning_loop_node.tests': ['test_data/*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'alive-progress>=2.1.0,<3.0.0',
 'async_generator>=1.10,<2.0',
 'fastapi-socketio>=0.0.6,<0.0.7',
 'fastapi-utils>=0.2.1,<0.3.0',
 'fastapi>=0.70.1,<0.71.0',
 'icecream>=2.1.0,<3.0.0',
 'numpy>=1.13.3,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pytest-watch>=4.2.0,<5.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'python-socketio[asyncio_client]>=5.0.4,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'simplejson>=3.17.2,<4.0.0',
 'uvicorn>=0.13.3,<0.14.0',
 'werkzeug>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'learning-loop-node',
    'version': '0.7.2',
    'description': 'Python Library for Nodes which connect to the Zauberzeug Learning Loop',
    'long_description': '# Learning Loop Node\n\nThis Python library helps you to write your own Detection Nodes, Training Nodes and Converter Nodes for the Zauberzeug Learning Loop.\n\n## General Usage\n\nYou can configure connection to our Learning Loop by specifying the following environment variables before starting:\n\n- LOOP_HOST=learning-loop.ai\n- LOOP_USERNAME=<your username>\n- LOOP_PASSWORD=<your password>\n\n## Detector Node\n\nDetector Nodes are normally deployed on edge devices like robots or machinery but can also run in the cloud to provide backend services for an app or similar. These nodes register themself at the Learning Loop to make model deployments very easy. They also provide REST and Socket.io APIs to run inferences. By default the images will automatically used for active learning: high uncertain predictions will be submitted to the Learning Loop inbox.\n\n#### Additinal environment variables\n\n- LOOP_ORGANIZATION=<your organization>\n- LOOP_PROJECT=<your project>\n\n## Trainer Node\n\nTrainers fetch the images and anntoations from the Learning Loop to generate new and improved models.\n\n- if the command line tool "jpeginfo" is installed, the downloader will drop corrupted images automatically\n\n## Converter Node\n\nA Conveter Node converts models from one format into another.\n\n### How to test the operability?\n\nAssumend there is a Converter Node which converts models of format \'format_a\' into \'format_b\'.\nUpload a model with\n`curl --request POST -F \'files=@my_model.zip\' https://learning-loop.ai/api/zauberzeug/projects/demo/format_a`\nThe model should now be available for the format \'format_a\'\n`curl "https://learning-loop.ai/api/zauberzeug/projects/demo/models?format=format_a"`\n\n```\n{\n  "models": [\n    {\n      "id": "3c20d807-f71c-40dc-a996-8a8968aa5431",\n      "version": "4.0",\n      "formats": [\n        "format_a"\n      ],\n      "created": "2021-06-01T06:28:21.289092",\n      "comment": "uploaded at 2021-06-01 06:28:21.288442",\n      ...\n    }\n  ]\n}\n\n```\n\nbut not in the format_b\n`curl "https://learning-loop.ai/api/zauberzeug/projects/demo/models?format=format_b"`\n\n```\n{\n  "models": []\n}\n```\n\nConnect the Node to the Learning Loop by simply starting the container.\nAfter a short time the converted model should be available as well.\n`curl https://learning-loop.ai/api/zauberzeug/projects/demo/models?format=format_b`\n\n```\n{\n  "models": [\n    {\n      "id": "3c20d807-f71c-40dc-a996-8a8968aa5431",\n      "version": "4.0",\n      "formats": [\n        "format_a",\n        "format_b",\n      ],\n      "created": "2021-06-01T06:28:21.289092",\n      "comment": "uploaded at 2021-06-01 06:28:21.288442",\n      ...\n    }\n  ]\n}\n```\n\n## About Models (the currency between Nodes)\n\n- Models are packed in zips and saved on the Learning Loop (one for each format)\n- Nodes and users can upload and download models with which they want to work\n- In each zip there is a file called `model.json` which contains the metadata to interpret the other files in the package\n- for base models (pretrained models from external sources) no `model.json` has to be sent, ie. these models should simply be zipped in such a way that the respective trainer can work with them.\n- the loop adds or corrects the following properties in the `model.json` after receiving; it also creates the file if it is missing:\n  - `host`: uri to the loop\n  - `organization`: the ID of the organization\n  - `project`: the id of the project\n  - `version`: the version number that the loop assigned for this model (e.g. 1.3)\n  - `id`: the model UUID (currently not needed by anyone, since host, org, project, version clearly identify the model)\n  - `format`: the format e.g. yolo, tkdnn, yolor etc.\n- Nodes add properties to `model.json`, which contains all the information which are needed by subsequent nodes. These are typically the properties:\n  - `resolution`: resolution in which the model expects images (as `int`, since the resolution is mostly square - later, ` resolution_x`` resolution_y ` would also be conceivable or `resolutions` to give a list of possible resolutions)\n  - `categories`: list of categories with name, id, (later also type), in the order in which they are used by the model -- this is neccessary to be robust about renamings\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/learning_loop_node',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.9,<4.0.0',
}


setup(**setup_kwargs)
