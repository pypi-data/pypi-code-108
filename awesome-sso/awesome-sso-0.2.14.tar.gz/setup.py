# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awesome_sso',
 'awesome_sso.exceptions',
 'awesome_sso.mail',
 'awesome_sso.service',
 'awesome_sso.service.notification',
 'awesome_sso.service.user',
 'awesome_sso.store',
 'awesome_sso.util']

package_data = \
{'': ['*']}

install_requires = \
['APScheduler>=3.8.1,<4.0.0',
 'PyJWT>=2.3.0,<3.0.0',
 'bcrypt>=3.2.0,<4.0.0',
 'beanie>=1.8.0,<2.0.0',
 'cryptography>=36.0.0,<37.0.0',
 'fastapi>=0.70.0,<0.71.0',
 'minio>=7.1.1,<8.0.0',
 'pandas>=1.3.5,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pydantic[email]>=1.8.2,<2.0.0',
 'uvicorn>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'awesome-sso',
    'version': '0.2.14',
    'description': 'sso general utility for services connected to sso',
    'long_description': '[![Stable Version](https://img.shields.io/pypi/v/awesome-sso?label=stable)](https://pypi.org/project/awesome-sso/)\n[![tests](https://github.com/MoBagel/awesome-sso/workflows/ci/badge.svg)](https://github.com/MoBagel/awesome-sso)\n[![Coverage Status](https://coveralls.io/repos/github/MoBagel/awesome-sso/badge.svg?branch=develop)](https://coveralls.io/github/MoBagel/awesome-sso)\n\n# Awesome SSO\n\nA library designed to host common components for a cluster of microservices sharing a single sign on.\n\n## Feature\n\n- [x] A common exception class, supporting both status code and custom error code to map to more detailed error message\n  or serve as i18n key.\n- [x] A common FastAPI app for interaction with service, like login ,registration and unregistration.\n- [x] a connector for minio object store.\n- [x] a connector for beanie, a mongo odm compatible with pydantic.\n\n## Usage\n\n### Installation\n\n1. `pip install awesome-sso`\n\n### Exceptions\n\nUsing fast API as example, we may simply throw exception with a proper status code, and an optional error code. We may\nalso supply arbitrary key value in args dict, to help frontend render better error message.\n\n```python\nfrom awesome_sso.exceptions import NotFound\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n\n@router.get(\'/transactions\')\ndef get(id: str):\n    try:\n        obj = find_by_id(id)\n    except Exception as e:\n        raise NotFound(message=\'transaction not found\' % id, error_code=\'A0001\', args={id: id})\n    ...\n```\n\nAnd we may implement a common error handler to convert all these errors to proper response schema\n\n```python\nfrom awesome_sso.exceptions import HTTPException\nfrom fastapi.requests import Request\nfrom fastapi.responses import JSONResponse\n\n\n@app.exception_handler(HTTPException)\nasync def http_exception_handler(request: Request, exc: HTTPException):\n    return JSONResponse(\n        status_code=exc.status_code,\n        content={\n            \'detail\': exc.detail,\n            \'error_code\': exc.error_code,\n        }\n    )\n```\n\nThis would result in a response with status code 404, and body\n\n```json\n{\n  "status_code": 404,\n  "detail": {\n    "message": "transaction not found",\n    "id": "some_id"\n  },\n  "error_code": "A0001"\n}\n```\n\nWith this response, frontend can decide to simply render detail, or map it to detailed message. If error_code "A0001"\ncorrespond to the following i18 n entry\n\n```json\n"error.A0001": {"en-US": "transaction can not be found with supplied {id}: {message}"}\n```\n\nwe may format message accordingly with\n\n```typescript\nerrorMessage = formatMessage({ id: `error.${error.data.error_code}` }, error.data.detail);\n```\n\nNote that error code is not supplied, is default to status code. So it is always safe to simply use error_code in\nfrontend to decide what to render.\n\n### Data Store\n\n#### Minio\n\nrefer to `tests/test_minio.py`\n\n#### Mongo\n\nrefer to `tests/service/test_user.py`\n\n```python\nfrom beanie import init_beanie\nfrom motor.motor_asyncio import AsyncIOMotorClient\nfrom awesome_sso.service.user.schema import AwesomeUser\n\n\ndef init_mongo():\n    settings = YOUR_SETTINGS()\n    models = [AwesomeUser]\n    cli = AsyncIOMotorClient(settings.mongodb_dsn)\n    await init_beanie(\n        database=cli[settings.mongodb_db_name],\n        document_models=models,\n    )\n    for model in models:\n        await model.get_motor_collection().drop()\n        await model.get_motor_collection().drop_indexes()\n```\n\n### Service\n\n#### configure service settings\n\n```python\nfrom awesome_sso.service.settings import Settings\n\nsettings = Settings()\nsettings.init_app(\n    symmetric_key=\'YOUR_SYMMETRIC_KEY\',  # to encode and decode service token\n    public_key=\'YOUR_PUBLIC_KEY\',  # to decode the token signed by sso\n    user_model=USER_MODEL,  # user orm needs to inherit AwesomeUser from `awesome_sso.user.schema`\n    service_name=\'YOUR_SERVICE_NAME\',  # for service discovery, to recognize service\n    sso_domain=\'YOUR_SSO_DOMAIN\',  # for service registration and sync user\n)\n\n```\n\n#### initial service and mount to your application\n\n```python\nfrom awesome_sso.service import Service\nfrom fastapi import FastAPI\n\napp = FastAPI()\nservice = Service()\nservice.init_app(YOUR_FASTAPI_APP)\napp.mount(\'/YOUR/PATH\', YOUR_FASTAPI_APP)\n```\n\nthen open the api doc, you will see the apis in `awesome_sso.service.user.route`\n\n## Development\n\n### Installing Poetry\n\n1. create your own environment for poetry, and simply run: `pip install poetry`\n2. alternatively, you can refer to [poetry\'s official page](https://github.com/python-poetry/poetry)\n3. to be able to use `poe` directly, `pip install poethepoet`\n\n### Contributing\n\n1. project setup: `poetry install`\n2. create your own branch to start developing new feature.\n3. before creating pr, make sure you pass `poe lint` and `./run_test.sh`.\n    - what happened inside `./run_test.sh` is that a minio server is setup for you temporarily, and teardown and unit\n      test is finished.\n    - notice that `poe test` would also work if you already have a minio up and running. You need the following env\n      variable: `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_ADDRESS` upon running `poe test`.\n4. for a list of available poe command, `poe`\n5. after you submit a pr, you should check if pipeline is successful.\n\n### Releasing\n\n1. `poetry version [new_version]`\n2. `git commit -m"Bump version"`\n3. `git push origin develop`\n4. [create new release](https://github.com/MoBagel/awesome-sso/releases/new) on github.\n5. Create release off develop branch, auto generate notes, and review release note. \n6. Publish release\n\n',
    'author': 'Schwannden Kuo',
    'author_email': 'schwannden@mobagel.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MoBagel/awesome-sso',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
