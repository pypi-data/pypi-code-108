# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deafadder_container']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'deafadder-container',
    'version': '0.5.0',
    'description': 'A dependency injection tools and container manager for python',
    'long_description': ".. image:: https://circleci.com/gh/deaf-adder/deafadder-container/tree/master.svg?style=svg&circle-token=16b2bcd2e9f92ee31a92571b05ab75929085ab38\n        :target: https://circleci.com/gh/deaf-adder/deafadder-container/tree/master\n\n\ndeafadder-container\n===================\n\n    A container library to manage dependencies between services and component *à la spring*\n    but using :code:`metaclass`.\n\nThis library provide a way to manage :code:`Components` in a python application.\nA :code:`Component` being a kind of singleton (meaning, unless specified, it will be a singleton) that can automatically link (inject) dependencies if\nthose dependencies are other v`Components`.\n\nFor those familiar with Java, the base idea comes from Spring where it is easy to inject Components into other Components without having to deal with\nthe all the manual wiring and object initialization. While this library as been inspired by the autowiring mechanism of Spring, it is still immature,\nwith a reduced scope and present some limitation (due to :code:`metaclass`). While some limitation are expected to change in future version, it's future is still\nuncertain, so use with caution.\n\n\nDocumentation\n-------------\n\nJust follow this link: https://deaf-adder.github.io/deafadder-container/#/\n\nFancy a more example base approach ? The documentation is full of examples and the tests files should be enough to have a better understanding of\nwhat can be achieved.\n\nExpected future developments\n----------------------------\n\n- getting rid of the :code:`metaclass` to achieve the same, or similar, result *(why ? Because I'd like to include dependency injection based on ABC class\n  which are :code:`metaclass` and one object could not extends an ABC class and be have a :code:`Component` metaclass as well)*\n- add a section to present projects build around this library\n\n",
    'author': 'Leddzip',
    'author_email': 'leddzip@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/deaf-adder/deafadder-container',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
