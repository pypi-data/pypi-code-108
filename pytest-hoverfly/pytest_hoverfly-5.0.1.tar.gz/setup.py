# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_hoverfly']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3', 'pytest>=5.0', 'requests>=2.22.0', 'typing_extensions>=3.7.4']

entry_points = \
{'pytest11': ['hoverfly = pytest_hoverfly.pytest_hoverfly']}

setup_kwargs = {
    'name': 'pytest-hoverfly',
    'version': '5.0.1',
    'description': 'Simplify working with Hoverfly from pytest',
    'long_description': "[![CI](https://github.com/wrike/pytest-hoverfly/actions/workflows/main.yml/badge.svg)](https://github.com/wrike/pytest-hoverfly/actions/workflows/main.yml)\n\n\nA helper for working with [Hoverfly](https://hoverfly.readthedocs.io/en/latest/) from `pytest`. Works both locally and in CI.\n\n### Installation\n`pip install pytest-hoverfly`\n\nor\n\n`poetry add pytest-hoverfly --dev`\n\n\n### Usage\nThere are two use cases: to record a new test and to use recordings.\n\n#### Prerequisites\nYou need to have [Docker](https://www.docker.com/) installed. `pytest-hoverfly` uses it under the hood to create Hoverfly instances.\n\nCreate a directory to store simulation files. Pass `--hoverfly-simulation-path` option\nwhen calling `pytest`. The path may be absolute or relative to your `pytest.ini` file.\nE.g. if you have a structure like this:\n```\n├── myproject\n    ├── ...\n├── pytest.ini\n└── tests\n    ├── conftest.py\n    ├── simulations\n```\n\nThen put this in you pytest.ini:\n```\n[pytest]\naddopts =\n    --hoverfly-simulation-path=tests/simulations\n```\n\n#### Without Docker Desktop\nIf you're using something like [lima](https://github.com/lima-vm/lima) instead of Docker Desktop, you need to specify a path to Docker API. For lima:\n\n`export DOCKER_HOST=unix:///Users/<YOUR-USER>/.lima/default/sock/docker.sock`\n\nIf you're using [minikube](https://github.com/kubernetes/minikube) instead of Docker Desktop, you need to specify the service host because the exposed ports are not available on localhost. For minikube you get the service IP with `minikube ip` command and then put it in the env var:\n\n`export SERVICE_HOST=192.168.0.xxx`\n\n#### How to record a test\n```python\nfrom pytest_hoverfly import hoverfly\nimport requests\n\n\n@hoverfly('my-simulation-file', record=True)\ndef test_google_with_hoverfly():\n    assert requests.get('https://google.com').status_code == 200\n```\n\nWrite a test. Decorate it with `@hoverfly`, specifying a name of a file to save the simulation to.\nRun the test. A Hoverfly container will be created, and  `HTTP_PROXY` and `HTTPS_PROXY` env vars\nwill be set to point to this container. After test finishes, the resulting simulation will\nbe exported from Hoverfly and saved to a file you specified. After test session ends, Hoverfly\ncontainer will be destroyed (unless `--hoverfly-reuse-container` is passed to pytest).\n\nThis will work for cases when a server always returns the same response for the same\nrequest. If you need to work with stateful endpoints (e.g. wait for Teamcity build\nto finish), use `@hoverfly('my-simulation, record=True, stateful=True)`. See\n[Hoverfly docs](https://docs.hoverfly.io/en/latest/pages/tutorials/basic/capturingsequences/capturingsequences.html)\nfor details.\n\n#### How to use recordings\nRemove `record` parameter. That's it. When you run the test, it will create a container\nwith Hoverfly, upload your simulation into it, and use it instead of a real service.\n\n```python\nfrom pytest_hoverfly import hoverfly\nimport requests\n\n\n@hoverfly('my-simulation-file')\ndef test_google_with_hoverfly():\n    assert requests.get('https://google.com').status_code == 200\n```\n\nCaveat: if you're using an HTTP library other than `aiohttp` or `requests` you need to\ntell it to use Hoverfly as HTTP(S) proxy and to trust Hoverfly's certificate. See\n`_patch_env` fixture for details on how it's done for `aiohttp` and `requests`.\n\n#### How to re-record a test\nAdd `record=True` again, and run the test. The simulation file will be overwritten.\n\n\n#### Change Hoverfly version\nTo use a different Hoverfly version, specify `--hoverfly-image`. It must be a valid Docker image tag.\n\n#### Start Hoverfly with custom parameters\nUse `--hoverfly-args`. It is passed as is to a Hoverfly container.\n\n### Usage in CI\nCI systems like Gitlab CI or Github Actions allow you to run arbitrary services as containers. `pytest-hoverfly` can detect if a Hoverfly instance is already running by looking at certain environment variables. If it detects a running instance, `pytest-hovefly` uses it, and doesn't create a new container.\n\nFor Github Actions:\n\n```\nservices:\n  hoverfly:\n    image: spectolabs/hoverfly:v1.3.2\n    ports:\n      - 8500:8500\n      - 8888:8888\n\n  env:\n    HOVERFLY_HOST: localhost\n    HOVERFLY_PROXY_PORT: 8500\n    HOVERFLY_ADMIN_PORT: 8888\n```\n\nMind that all three variables must be specified.\n",
    'author': 'Devops team at Wrike',
    'author_email': 'devops@team.wrike.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wrike/pytest-hoverfly',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
