# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cuddle']

package_data = \
{'': ['*']}

install_requires = \
['regex>=2021.8.28,<2022.0.0', 'tatsu>=5.6.1,<6.0.0']

setup_kwargs = {
    'name': 'cuddle',
    'version': '1.0.6',
    'description': 'A Python library for the KDL Document Language.',
    'long_description': '# python-cuddle\n\n[![CI](https://github.com/djmattyg007/python-cuddle/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/djmattyg007/python-cuddle/actions/workflows/ci.yml)\n\nA Python library for the [KDL Document Language](https://github.com/kdl-org/kdl).\n\n## Install\n\n```shell\npip install cuddle\n```\n\nOr if you\'re using poetry:\n\n```shell\npoetry add cuddle\n```\n\nCuddle supports Python 3.9 and above. \n\n## Usage\n\n```python\nfrom cuddle import Document, Node, NodeList, dumps, loads\n\nloaded_doc = loads(\'\'\'// Nodes can be separated into multiple lines\ntitle \\\n  "Some title"\n\n// Nested nodes are fully supported\ncontents {\n  section "First section" {\n    paragraph "This is the first paragraph"\n    paragraph "This is the second paragraph"\n  }\n}\n\n// Files must be utf8 encoded!\nsmile "😁"\n\n// Instead of anonymous nodes, nodes and properties can be wrapped\n// in "" for arbitrary node names.\n"!@#$@$%Q#$%~@!40" "1.2.3" "!!!!!"=true\n\n// The following is a legal bare identifier:\nfoo123~!@#$%^&*.:\'|/?+ "weeee"\n\n// And you can also use unicode!\nノード\u3000お名前="☜(ﾟヮﾟ☜)"\n\n// kdl specifically allows properties and values to be\n// interspersed with each other, much like CLI commands.\nfoo bar=true "baz" quux=false 1 2 3\n\'\'\')\nprint(dumps(loaded_doc))\n\nprint()\n\n# Creating documents from scratch is a bit verbose\nnodes = []\nchild_node = Node("complex name here!", None)\nnodes.append(\n    Node("simple-name", None, arguments=[123], children=[child_node])\n)\nnodes.append(\n    Node("second-node", None, properties={"key": "value"})\n)\nnode_list = NodeList(nodes)\ndoc = Document(node_list)\nprint(dumps(doc))\n```\n\nThe output:\n\n```\ntitle "Some title"\nsmile "😁"\n!@#$@$%Q#$%~@!40 !!!!!=true "1.2.3"\nfoo123~!@#$%^&*.:\'|/?+ "weeee"\nノード お名前="☜(ﾟヮﾟ☜)"\nfoo bar=true quux=false "baz" 1 2 3\n\nsimple-name 123 {\n  "complex name here!"\n}\nsecond-node key="value"\n```\n\n## License\n\nThe code is available under the [MIT license](LICENSE.txt).\n',
    'author': 'Matthew Gamble',
    'author_email': 'git@matthewgamble.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/djmattyg007/python-cuddle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
