# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['meilisearch_fastapi',
 'meilisearch_fastapi.models',
 'meilisearch_fastapi.routes']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.65.1,<0.74.0',
 'meilisearch-python-async>=0.22.0,<0.23.0',
 'pydantic[dotenv]>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'meilisearch-fastapi',
    'version': '0.13.0',
    'description': 'MeiliSearch integration with FastAPI',
    'long_description': '# MeiliSearch FastAPI\n\n![CI Status](https://github.com/sanders41/meilisearch-fastapi/workflows/CI/badge.svg?branch=main&event=push)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sanders41/meilisearch-fastapi/main.svg)](https://results.pre-commit.ci/latest/github/sanders41/meilisearch-fastapi/main)\n[![Coverage](https://codecov.io/gh/sanders41/meilisearch-fastapi/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/gh/sanders41/meilisearch-fastapi)\n[![PyPI version](https://badge.fury.io/py/meilisearch-fastapi.svg)](https://badge.fury.io/py/meilisearch-fastapi)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/meilisearch-fastapi?color=5cc141)](https://github.com/sanders41/meilisearch-fastapi)\n\nMeiliSearch FastAPI provides [FastAPI](https://fastapi.tiangolo.com/) routes for interacting with [MeiliSearch](https://www.meilisearch.com/).\n\n## Installation\n\nUsing a virtual environmnet is recommended for installing this package. Once the virtual environment is created and activated install the package with:\n\n```sh\npip install meilisearch-fastapi\n```\n\n## Useage\n\nRoutes are split in groups so that different dependencies can be injected, and therefore different levels of access, can be given to different groups of routes.\n\n### Example with no authentication require for routes\n\n```py\nfrom fastapi import APIRouter, FastAPI\nfrom meilisearch_fastapi.routes import (\n    document_routes,\n    index_routes,\n    meilisearch_routes,\n    search_routes,\n    settings_routes,\n)\n\napp = FastAPI()\napi_router = APIRouter()\napi_router.include_router(document_routes.router, prefix="/documents")\napi_router.include_router(index_routes.router, prefix="/indexes")\napi_router.include_router(meilisearch_routes.router, prefix="/meilisearch")\napi_router.include_router(search_routes.router, prefix="/search")\napi_router.include_router(settings_routes.router, prefix="/settings")\n\napp.include_router(api_router)\n```\n\n### Example with routes requiring authentication\n\n```py\nfrom fastapi import APIRouter, FastAPI\nfrom meilisearch_fastapi import routes\n\nfrom my_app import my_authentication\n\napp = FastAPI()\napi_router = APIRouter()\napi_router.include_router(document_routes.router, prefix="/documents", dependeincies=[Depends(my_authentication)])\napi_router.include_router(index_routes.router, prefix="/indexes", dependeincies=[Depends(my_authentication)])\napi_router.include_router(meilisearch_routes.router, prefix="/meilisearch", dependeincies=[Depends(my_authentication)])\napi_router.include_router(search_routes.router, prefix="/search", dependeincies=[Depends(my_authentication)])\napi_router.include_router(settings_routes.router, prefix="/settings", dependeincies=[Depends(my_authentication)])\n\napp.include_router(api_router)\n```\n\nThe url for MeiliSearch, weather an https address should be used, and API key are read from\nenvironment variables. Putting these into a .env file will keep you from having to set these\nvariables each time the terminal is restarted.\n\n```txt\nMEILI_HTTP_ADDR=localhost:7700  # This is the url for your instance of MeiliSearch\nMEILI_HTTPS_URL=true  # Setting this specifies the address should be https://. If false or not included the address will be http://\nMEILI_MASTER_KEY=masterKey  # This is the API key for your MeiliSearch instance\n```\n\nNow the MeiliSearch routes will be available in your FastAPI app. Documentation for the routes can be viewed in the OpenAPI documentation of the FastAPI app. To view this start your FastAPI app and naviate to the docs `http://localhost:8000/docs` replacing the url with the correct url for your app.\n\n## Compatibility with MeiliSearch\n\nThis package only guarantees the compatibility with [version v0.25 of MeiliSearch](https://github.com/meilisearch/MeiliSearch/releases/tag/v0.25.0).\n\n## Contributing\n\nContributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)\n',
    'author': 'Paul Sanders',
    'author_email': 'psanders1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sanders41/meilisearch-fastapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
