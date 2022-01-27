# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['emmett',
 'emmett.asgi',
 'emmett.asgi.loops',
 'emmett.asgi.protocols',
 'emmett.asgi.protocols.http',
 'emmett.asgi.protocols.ws',
 'emmett.assets',
 'emmett.assets.debug',
 'emmett.language',
 'emmett.libs',
 'emmett.orm',
 'emmett.orm.engines',
 'emmett.orm.migrations',
 'emmett.routing',
 'emmett.templating',
 'emmett.testing',
 'emmett.tools',
 'emmett.tools.auth',
 'emmett.validators',
 'emmett.wrappers',
 'tests']

package_data = \
{'': ['*'], 'tests': ['languages/*', 'templates/*', 'templates/auth/*']}

install_requires = \
['click>=6.0',
 'h11>=0.12.0,<0.13.0',
 'h2>=3.2.0,<4.1.0',
 'pendulum>=2.1.2,<2.2.0',
 'pyDAL==17.3',
 'pyaes>=1.6.1,<1.7.0',
 'python-rapidjson>=1.0,<2.0',
 'pyyaml>=5.4,<6.0',
 'renoir>=1.5,<2.0',
 'severus>=1.1,<2.0',
 'uvicorn==0.16.0',
 'websockets>=10.0,<11.0']

extras_require = \
{':sys_platform != "win32"': ['httptools>=0.3.0,<0.4.0',
                              'uvloop>=0.16.0,<0.17.0'],
 'crypto': ['emmett-crypto>=0.2.0,<0.3.0'],
 'orjson': ['orjson>=3.6.5,<3.7.0']}

entry_points = \
{'console_scripts': ['emmett = emmett.cli:main']}

setup_kwargs = {
    'name': 'emmett',
    'version': '2.4.2',
    'description': 'The web framework for inventors',
    'long_description': '![Emmett](https://deneb.spaces.amira.io/emmett/artwork/logo-bwb-xb-xl.png)\n\nEmmett is a full-stack Python web framework designed with simplicity in mind.\n\nThe aim of Emmett is to be clearly understandable, easy to be learned and to be \nused, so you can focus completely on your product\'s features:\n\n```python\nfrom emmett import App, request, response\nfrom emmett.orm import Database, Model, Field\nfrom emmett.tools import service, requires\n\nclass Task(Model):\n    name = Field.string()\n    is_completed = Field.bool(default=False)\n\napp = App(__name__)\napp.config.db.uri = "postgres://user:password@localhost/foo"\ndb = Database(app)\ndb.define_models(Task)\napp.pipeline = [db.pipe]\n\ndef is_authenticated():\n    return request.headers["Api-Key"] == "foobar"\n    \ndef not_authorized():\n    response.status = 401\n    return {\'error\': \'not authorized\'}\n\n@app.route(methods=\'get\')\n@service.json\n@requires(is_authenticated, otherwise=not_authorized)\nasync def todo():\n    page = request.query_params.page or 1\n    tasks = Task.where(\n        lambda t: t.is_completed == False\n    ).select(paginate=(page, 20))\n    return {\'tasks\': tasks}\n```\n\n[![pip version](https://img.shields.io/pypi/v/emmett.svg?style=flat)](https://pypi.python.org/pypi/emmett)\n![Tests Status](https://github.com/emmett-framework/emmett/workflows/Tests/badge.svg)\n\n## Documentation\n\nThe documentation is available at [https://emmett.sh/docs](https://emmett.sh/docs).\nThe sources are available under the [docs folder](https://github.com/emmett-framework/emmett/tree/master/docs).\n\n## Examples\n\nThe *bloggy* example described in the [Tutorial](https://emmett.sh/docs/latest/tutorial) is available under the [examples folder](https://github.com/emmett-framework/emmett/tree/master/examples). \n\n## Status of the project\n\nEmmett is production ready and is compatible with Python 3.7 and above versions.\n\nEmmett follows a *semantic versioning* for its releases, with a `{major}.{minor}.{patch}` scheme for versions numbers, where:\n\n- *major* versions might introduce breaking changes\n- *minor* versions usually introduce new features and might introduce deprecations\n- *patch* versions only introduce bug fixes\n\nDeprecations are kept in place for at least 3 minor versions, and the drop is always communicated in the [upgrade guide](https://emmett.sh/docs/latest/upgrading).\n\n## How can I help?\n\nWe would be very glad if you contributed to the project in one or all of these ways:\n\n* Talking about Emmett with friends and on the web\n* Adding issues and features requests here on GitHub\n* Participating in discussions about new features and issues here on GitHub\n* Improving the documentation\n* Forking the project and writing beautiful code\n\n## License\n\nEmmmett is released under the BSD License.\n\nHowever, due to original license limitations, some components are included \nin Emmett under their original licenses. Please check the LICENSE file for \nmore details.\n',
    'author': 'Giovanni Barillari',
    'author_email': 'gi0baro@d4net.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://emmett.sh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
