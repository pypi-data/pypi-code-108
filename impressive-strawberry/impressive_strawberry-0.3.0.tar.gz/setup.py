# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['impressive_strawberry',
 'impressive_strawberry.database',
 'impressive_strawberry.database.alembic',
 'impressive_strawberry.database.alembic.versions',
 'impressive_strawberry.web',
 'impressive_strawberry.web.crud',
 'impressive_strawberry.web.deps',
 'impressive_strawberry.web.errors',
 'impressive_strawberry.web.handlers',
 'impressive_strawberry.web.models',
 'impressive_strawberry.web.responses',
 'impressive_strawberry.web.routes',
 'impressive_strawberry.web.routes.api.achievement.v1',
 'impressive_strawberry.web.routes.api.application.v1',
 'impressive_strawberry.web.routes.api.group.v1',
 'impressive_strawberry.web.routes.api.unlock.v1',
 'impressive_strawberry.web.routes.api.user.v1',
 'impressive_strawberry.web.routes.api.webhook.v1',
 'impressive_strawberry.web.testing',
 'impressive_strawberry.webhooks']

package_data = \
{'': ['*'], 'impressive_strawberry.web': ['templates/*']}

install_requires = \
['SQLAlchemy>=1.4.26,<2.0.0',
 'alembic>=1.7.4,<2.0.0',
 'fastapi>=0.70.0,<0.71.0',
 'httpx>=0.21.1,<0.22.0',
 'lazy-object-proxy>=1.6.0,<2.0.0',
 'psycopg2-binary>=2.9.1,<3.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'python-dotenv>=0.19.1,<0.20.0',
 'uvicorn>=0.15.0,<0.16.0']

setup_kwargs = {
    'name': 'impressive-strawberry',
    'version': '0.3.0',
    'description': 'Achievements-as-a-service',
    'long_description': "# Impressive Strawberry\n\n_Achievements-as-a-service_\n\n## About\n\nImpressive Strawberry is a Web API that allows the consumer applications to manage user-unlockable achievements, and for external applications to unlock them\nfor the users, notifying them in the process.\n\n## Development\n\n### Design document\n\nThe design document was made [on FigJam](https://www.figma.com/file/8J7exqW3srh0WNiICHnf0O/Medals?node-id=0%3A1).\n\n### Documentation\n\nDocumentation is made available [via GitHub Pages](https://hub.ryg.one/impressive-strawberry/).\n\n### Tasks\n\nTasks to be done are published [on GitHub Issues](https://github.com/RYGhub/impressive-strawberry/issues).\n\nIf you **find a bug**, a **mistake**, or want to **suggest a new feature**,\nplease [create a new issue](https://github.com/RYGhub/impressive-strawberry/issues/new)!\n\n### Pull requests\n\nFeel free to fork the project and continue developing it, but remember to [respect the AGPL 3.0+ license](LICENSE.txt)!\n\nIf you want to contribute back to the main branch, please [open a new pull request](https://github.com/RYGhub/impressive-strawberry/pulls)!\n\n### Discussion\n\nA forum about the project is available [on GitHub Discussions](https://github.com/RYGhub/impressive-strawberry/discussions).\n\nIf you want to **talk about the project**, or **ask a question** or even **help**,\nplease [create a new discussion](https://github.com/RYGhub/impressive-strawberry/discussions/new)!\n\n### CI / CD\n\nCI and CD for this project is hosted [on GitHub Actions](https://github.com/RYGhub/impressive-strawberry/actions).\n\n[![🔨 Steffo's Python Poetry Workflow](https://github.com/RYGhub/impressive-strawberry/actions/workflows/stefflow.yml/badge.svg)](https://github.com/RYGhub/impressive-strawberry/actions/workflows/stefflow.yml)\n\n#### Jobs\n\n- _Tests_ are run **on every push** and **on every pull request**.\n- _CodeQL_ is run **every monday at 10:10 AM**.\n- _Build and publish_ are run **on every release**.\n\nAll jobs can be triggered simultaneously by pressing the **Run Workflow**\nbutton [on the Workflow page](https://github.com/RYGhub/impressive-strawberry/actions/workflows/stefflow.yml).\n\n### Roadmap\n\nThe roadmap is published [on GitHub Projects](https://github.com/orgs/RYGhub/projects/1/views/1).\n\n### Security\n\nPlease report security vulnerabilities via email at `security@steffo.eu`.\n",
    'author': 'Stefano Pigozzi',
    'author_email': 'me@steffo.eu',
    'maintainer': 'Stefano Pigozzi',
    'maintainer_email': 'me@steffo.eu',
    'url': 'https://impressive-strawberry.ryg.one/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
