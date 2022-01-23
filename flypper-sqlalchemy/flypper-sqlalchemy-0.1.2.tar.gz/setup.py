# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flypper_sqlalchemy', 'flypper_sqlalchemy.storage']

package_data = \
{'': ['*']}

modules = \
['README', 'LICENSE']
install_requires = \
['SQLAlchemy>=1.3,<2.0', 'flypper>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'flypper-sqlalchemy',
    'version': '0.1.2',
    'description': 'Feature flags, with a GUI - SQL Alchemy backend',
    'long_description': '# flypper-sqlalchemy\n\nFlypper-sqlalchemy is a storage backend for the [flypper](https://github.com/nicoolas25/flypper) package.\n\nIt is backed by a RDBMS through the SQL-Alchemy library so it an be used in a distributed environment and be persisted across restarts.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install `flypper-sqlalchemy`.\n\n```bash\npip install flypper-sqlalchemy\n```\n\n## Usage\n\nBuild a storage backend:\n\n```python\nfrom flypper_sqlalchemy.storage.sqla import SqlAlchemyStorage\n\n# Create tables, make sure they are created, for instance with `create_all()`.\nSqlAlchemyStorage.build_flags_table(sqla_metadata=metadata)\nSqlAlchemyStorage.build_metadata_table(sqla_metadata=metadata)\n\nstorage = SqlAlchemyStorage(session=session_proxy)\n\n# Or instead, depending on the use-case:\n#\n# storage = SqlAlchemyStorage(engine=engine)\n)\n```\n\nUse it in the web UI:\n\n```python\nfrom flypper.wsgi.web_ui import FlypperWebUI\n\nweb_ui = FlypperWebUI(storage=storage)\n```\n\nUse it in your code:\n1. Build a client for your app\n2. Use a context\n\n```python\nfrom flypper.client import Client as FlypperClient\n\n# Once per thread\nflypper_client = FlypperClient(storage=storage, ttl=10)\n\n# Once per request\nflypper_context = FlypperContext(\n    client=flypper_client,\n    entries={"user_id": "42"},\n)\n\n# Every time you need\nflypper_context.is_enabled("flag_name")\nflypper_context.is_enabled(\n    "other_flag_name",\n    entries={"item_reference": "blue-shampoo"},\n)\n```\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'Nicolas Zermati',
    'author_email': 'nicoolas25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nicoolas25/flypper-sqlalchemy',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
