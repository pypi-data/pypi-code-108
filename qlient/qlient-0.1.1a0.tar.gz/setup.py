# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['qlient', 'qlient.schema']

package_data = \
{'': ['*']}

install_requires = \
['platformdirs>=2.4.1,<3.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'qlient',
    'version': '0.1.1a0',
    'description': 'A fast and modern graphql client designed with simplicity in mind.',
    'long_description': '# Qlient: Python GraphQL Client\n\n[![qlient-org](https://circleci.com/gh/qlient-org/python-qlient.svg?style=svg)](https://circleci.com/gh/qlient-org/python-qlient)\n[![pypi](https://img.shields.io/pypi/v/qlient.svg)](https://pypi.python.org/pypi/qlient)\n[![versions](https://img.shields.io/pypi/pyversions/qlient.svg)](https://github.com/qlient-org/python-qlient)\n[![license](https://img.shields.io/github/license/qlient-org/python-qlient.svg)](https://github.com/qlient-org/python-qlient/blob/master/LICENSE)\n\nA fast and modern graphql client designed with simplicity in mind.\n\n## Help\n\nSee [documentation](https://qlient-org.github.io/python-qlient/) for more details\n\n## Installation\n\n```shell script\npip install qlient\n```\n\n## Quick Start\n\n````python\nfrom qlient import Client, GraphQLResponse\n\nclient = Client("https://swapi-graphql.netlify.app/.netlify/functions/index")\n\nres: GraphQLResponse = client.query.film(\n    # swapi graphql input fields\n    id="ZmlsbXM6MQ==",\n\n    # qlient specific\n    _fields=["id", "title", "episodeID"]\n)\n\nprint(res.query)  # query film($id: ID) { film(id: $id) { id title episodeID } }\nprint(res.variables)  # {\'id\': \'ZmlsbXM6MQ==\'}\nprint(res.data)  # {\'film\': {\'id\': \'ZmlsbXM6MQ==\', \'title\': \'A New Hope\', \'episodeID\': 4}}\n````\n',
    'author': 'Daniel Seifert',
    'author_email': 'info@danielseifert.ch',
    'maintainer': 'Daniel Seifert',
    'maintainer_email': 'info@danielseifert.ch',
    'url': 'https://qlient-org.github.io/python-qlient/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
