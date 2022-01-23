# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flypper', 'flypper.entities', 'flypper.storage', 'flypper.wsgi']

package_data = \
{'': ['*'], 'flypper.wsgi': ['templates/*']}

modules = \
['README', 'LICENSE']
install_requires = \
['Jinja2>=3.0.0,<4.0.0', 'Werkzeug>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'flypper',
    'version': '0.1.1',
    'description': 'Flypper is a lightweight feature flag package that ships with a WSGI interface.',
    'long_description': '# Flypper: feature flags, with a GUI\n\nFlypper is a lightweight feature flag package that ships with a WSGI interface.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install `flypper`.\n\n```bash\npip install flypper\n```\n\nYou might want to install one of the following backends instead:\n\n* [`flypper-redis`](https://github.com/nicoolas25/flypper-redis) to store your flags in Redis\n* [`flypper-sqlalchemy`](https://github.com/nicoolas25/flypper-sqlalchemy) to store your flags in a RDBMS using SQL-Alchemy (work in progress)\n\n## Why\n\nFeature flags can be instrumental to how a team ships software.\n\nI have a hard take delegating such a critical part to a third-party.\nAlso, third-parties tends to grow a bigger feature set than the one I need,\nto have a per-seat pricing, and to ask for a [SSO tax](https://sso.tax/).\n\nFlypper aims at providing a simple feature flag library one could integrate\ndirectly to their application as a dependency. The feature set is purposedly\nsmall and will require some light work on your side to integrate.\n\nDifferences compared to other similar libraries are:\n\n* A scrappy web UI to manage the flags\n* An architecture aimed at being used on backends and front-ends\n* An efficient caching mecanism to avoid roundtrip to the database\n\n## Usage\n\nThe library works with 3 components:\n1. A **storage** backend, storing and retrieving flags in a durable way\n2. A **client**, acting as an efficient in-memory cache for reading flags\n3. A **context**, making flags consistents during its lifespan\n\n| Components and their roles |\n|---|\n| ![storage-client-context](https://user-images.githubusercontent.com/163953/138587140-e133ec12-6776-4bee-b80f-851eac7cb6a9.png) |\n\nHere is an example:\n\n```python\nfrom redis import Redis\n\nfrom flypper import Client as Flypper\nfrom flypper_redis.storage.redis import RedisStorage\n\n# Instanciate a *Storage*\nredis_storage = RedisStorage(\n    redis=Redis(host="localhost", port=6379, db=0),\n    prefix="flypper-demo",\n)\n\n# Instanciate a *Client*\nflypper = Flypper(storage=redis_storage)\n\n# Query flags\' statuses within a *Context*\nwith flypper(segment="professionals") as flags:\n    if flags.is_enabled("graceful_degradation"):\n        skip_that()\n    elif flags.is_enabled("new_feature", user="42"):\n        do_the_new_stuff()\n    else:\n        do_the_old_stuff()\n```\n\nThe web UI acts as a client and only needs a storage:\n\n```python\nfrom flypper.wsgi.web_ui import FlypperWebUI\n\nflypper_web_ui = FlypperWebUI(storage=redis_storage)\n```\n\n| Web UI |\n|---|\n| ![web-ui](https://user-images.githubusercontent.com/163953/138586961-d3cb5653-8713-4e3f-a60b-207bc5913a15.png) |\n\nThe web UI can then be mounted as you see fit,\nfor instance via [`DispatcherMiddleware`](https://werkzeug.palletsprojects.com/en/2.0.x/middleware/dispatcher/).\n\n```python\napp = DispatcherMiddleware(app, {"/flypper": flypper_web_ui})\n```\n\n⚠ Careful, you might need to wrap the `FlypperWebUI` with your own authentication layer,\nfor instance like [here](https://eddmann.com/posts/creating-a-basic-auth-wsgi-middleware-in-python/).\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n### Work in progress you can contribute to\n\n* Testing the web UI with [pytest and selenium](https://pytest-selenium.readthedocs.io/en/latest/user_guide.html)\n* Better support prefixes within the web UI, so redirections work\n* Write tutorials and recipes in the `docs/`\n\n### Upcoming feature ideas\n\n* Javascript SDK\n* Tracking flags usage efficiently\n* More storage backends\n\n## Credits\n\nInspiration was heavily taken from the following projects.\n\n* [flipper](https://github.com/jnunemaker/flipper)\n* [unleash](https://github.com/Unleash/unleash)\n* [flipper-client](https://github.com/carta/flipper-client)\n\nMany thanks to their authors, maintainers, and contributors.\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n\n\n',
    'author': 'Nicolas Zermati',
    'author_email': 'nicoolas25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nicoolas25/flypper',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
