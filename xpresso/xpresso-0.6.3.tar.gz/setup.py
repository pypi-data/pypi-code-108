# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xpresso',
 'xpresso._utils',
 'xpresso.binders',
 'xpresso.binders._extractors',
 'xpresso.binders._extractors.body',
 'xpresso.binders._extractors.params',
 'xpresso.binders._openapi_providers',
 'xpresso.binders._openapi_providers.body',
 'xpresso.binders._openapi_providers.params',
 'xpresso.dependencies',
 'xpresso.encoders',
 'xpresso.middleware',
 'xpresso.openapi',
 'xpresso.routing',
 'xpresso.security']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3,<4', 'di>=0.52,<0.53', 'pydantic>=1,<2', 'starlette>=0.16.0,<2']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3'],
 ':python_version < "3.9"': ['typing-extensions>=3']}

setup_kwargs = {
    'name': 'xpresso',
    'version': '0.6.3',
    'description': 'A developer centric, performant Python web framework',
    'long_description': '<p align="center">\n  <a href="https://www.xpresso-api.dev"><img src="https://github.com/adriangb/xpresso/raw/main/docs/assets/images/xpresso-title.png" alt="XPresso"></a>\n</p>\n\n<p align="center">\n<a href="https://github.com/adriangb/xpresso/actions?query=workflow%3ACI%2FCD+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/adriangb/xpresso/actions/workflows/workflow.yaml/badge.svg?event=push&branch=main" alt="Test">\n</a>\n<a href="https://codecov.io/gh/adriangb/xpresso" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/adriangb/xpresso?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/xpresso" target="_blank">\n    <img src="https://img.shields.io/pypi/v/xpresso?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/xpresso" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/xpresso.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\nXPresso is an ASGI web framework built on top of [Starlette], [Pydantic] and [di], with heavy inspiration from [FastAPI].\n\nSome of the standout features are:\n\n- ASGI support for high performance (within the context of Python web frameworks)\n- OpenAPI documentation generation\n- Automatic parsing and validation of request bodies and parameters, with hooks for custom extractors\n- Full support for [OpenAPI parameter serialization](https://swagger.io/docs/specification/serialization/)\n- Highly typed and tested codebase with great IDE support\n- A powerful dependency injection system, backed by [di]\n\n## Requirements\n\nPython 3.7+\n\n## Installation\n\n```shell\npip install xpresso\n```\n\nYou\'ll also want to install an ASGI server, such as [Uvicorn].\n\n```shell\npip install uvicorn\n```\n\n## Example\n\nCreate a file named `example.py`:\n\n```python\nfrom pydantic import BaseModel\nfrom xpresso import App, Path, FromPath, FromQuery\n\nclass Item(BaseModel):\n    item_id: int\n    name: str\n\nasync def read_item(item_id: FromPath[int], name: FromQuery[str]) -> Item:\n    return Item(item_id=item_id, name=name)\n\napp = App(\n    routes=[\n        Path(\n            "/items/{item_id}",\n            get=read_item,\n        )\n    ]\n)\n```\n\nRun the application:\n\n```shell\nuvicorn example:app\n```\n\nNavigate to [http://127.0.0.1:8000/items/123?name=foobarbaz](http://127.0.0.1:8000/items/123?name=foobarbaz) in your browser.\nYou will get the following JSON response:\n\n```json\n{"item_id":123,"name":"foobarbaz"}\n```\n\nNow navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to poke around the interactive [Swagger UI] documentation:\n\n![Swagger UI](docs/readme_example_swagger.png)\n\nFor more examples, tutorials and reference materials, see our [documentation].\n\n## Inspiration and relationship to other frameworks\n\nXPresso is mainly inspired by FastAPI.\nFastAPI pioneered several ideas that are core to XPresso\'s approach:\n\n- Leverage Pydantic for JSON parsing, validation and schema generation.\n- Leverage Starlette for routing and other low level web framework functionality.\n- Provide a simple but powerful dependency injection system.\n- Use that dependency injection system to provide extraction of request bodies, forms, query parameters, etc.\n\nXPresso takes these ideas and refines them by:\n\n- Decoupling the dependency injection system from the request/response cycle, leading to an overall much more flexible and powerful dependency injection system, packaged up as the standalone [di] library. This is how XPresso is able to provide [dependency injection into the application lifespan] and support for [multiple dependency scopes].\n- Making the extraction of data from requests an API available to other developers, enabling features like compatibility with libraries other than Pydantic or [MessagePack support] to be made available as 3rd party extensions instead of feature requests. All of this with full support for hooking into the OpenAPI documentation generation.\n- [Providing better support for `application/x-www-form-urlencoded` and `multipart/form-data` requests](https://xpresso-api.dev/latest/tutorial/forms/) by describing them with dataclasses or [Pydantic] models. This includes support for advanced use cases like extracting JSON from a form field.\n- Better performance by implementing [dependency resolution in Rust], [executing dependencies concurrently] and [controlling threading of sync dependencies on a per-dependency basis].\n- Allowing you to describe a single OpenAPI operation that accepts multiple content/types and extracting the right one based on headers\n- Giving you the ability to access and modify responses from within dependencies, allowing you to replace timing, tracing and logging middleware (which is routing ¨naive) with routing aware dependencies. No more middleware that accepts a regex pattern of paths!\n- Allowing dynamic building of security models triggered by lifespan events (you can load your Security model config from the enviroment at runtime).\n- Use of `Annotated` ([PEP 593]) instead of default values (`param: str = Query(...)`) which decouples the framework from Pydantic and enables a lot of the other features listed above and even allows you to make up your own markers to use if you make [custom Binders].\n\n[Starlette]: https://github.com/encode/starlette\n[Pydantic]: https://github.com/samuelcolvin/pydantic/\n[FastAPI]: https://github.com/adriangb/xpresso\n[di]: https://github.com/adriangb/di\n[Uvicorn]: http://www.uvicorn.org/\n[documentation]: https://www.xpresso-api.dev/\n[Swagger UI]: https://swagger.io/tools/swagger-ui/\n[dependency injection into the application lifespan]: https://xpresso-api.dev/latest/tutorial/lifespan\n[multiple dependency scopes]: https://xpresso-api.dev/latest/tutorial/dependencies/scopes/\n[MessagePack support]: https://xpresso-api.dev/latest/advanced/binders/#custom-binders-messagepack-body\n[dependency resolution in Rust]: https://github.com/adriangb/graphlib2\n[executing dependencies concurrently]: https://xpresso-api.dev/latest/advanced/dependencies/performance/#concurrent-execution\n[controlling threading of sync dependencies on a per-dependency basis]: https://xpresso-api.dev/latest/advanced/dependencies/performance/#sync-vs-async\n[PEP 593]: https://www.python.org/dev/peps/pep-0593/\n[custom Binders]: https://xpresso-api.dev/latest/advanced/binders/\n\nSee this release on GitHub: [v0.6.3](https://github.com/adriangb/di/releases/tag/0.6.3)\n',
    'author': 'Adrian Garcia Badaracco',
    'author_email': 'adrian@adriangb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adriangb/xpresso',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
