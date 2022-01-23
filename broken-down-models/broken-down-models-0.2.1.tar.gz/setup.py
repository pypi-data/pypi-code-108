# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bdmodels']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.2']

setup_kwargs = {
    'name': 'broken-down-models',
    'version': '0.2.1',
    'description': 'A set of utlities for breaking a large Django model down to separate components',
    'long_description': '.. image:: https://github.com/matific/broken-down-models/actions/workflows/tests.yml/badge.svg\n   :alt: Test status\n\n\nBreak a large model down, transparently\n---------------------------------------\n\nIn a project that goes on for several years, models tend to grow and\naccumulate fields. If you aren\'t very disciplined about this, you wake up\none day, and find that one of your central tables, one with millions of\nrows, has 43 columns, including some TextFields. Most of them are not\nrequired most of the time, but the default (and common) use is to fetch all\nof them; also, since this table is queried a lot, the mere fact that it has\nso many columns makes some of the access slower.\n\nWhen you realize that, you want to break it into components, such that\nonly a few, most-important columns will participate in the large searches,\nwhile further details will be searched and fetched only when needed.\n\nBut that is a scary proposition -- it might involve subtle code changes,\nbreak not just field access but also ORM queries... and this is a central\nmodel. The change imagined is open-heart surgery on a large project.\nMaybe, if we look the other way, it won\'t bother us too much...\n\n**broken-down-models** is here to help you. This is a library which can\nhelp you refactor your large model into a set of smaller ones, each with\nits own database table, while most of your project code remains unchanged.\n\nHow?\n----\n\nDjango already includes a mechanism where fields for one model are stored\nin more than one table: Multi Table Inheritance (also known as MTI).\nThat\'s what happens when we do "normal" inheritance of models, without\nspecifying anything special in the Meta of either of the models.\n\nPython also supports Multiple Inheritance -- one class can have many parent\nclasses. And this also works with Django\'s MTI -- we can have multiple MTI.\n\nUsually, when we think of a "core" set of attributes with different extensions,\nand we decide to implement it with MTI, we put this core set in a parent\nmodel, and make the extensions subclass it. But in the situation where we\ntry to break down an existing model, this would mean that code which currently\nuses the large model will have to change, to recognize the new parts.\n\n**broken-down-models** puts this idea on its head: The extensions become\nparent models, and the core set is defined in a model which inherits them all.\nThis way, all the fields are still fields of of the model we started with,\nfor all purposes -- including not just attribute access, but also ORM queries.\nFor this to really work well, though, some further modifications are required;\nthis is why the library exists, and it is explained in its documentation.\n',
    'author': 'Shai Berger',
    'author_email': 'shai.berger@slatescience.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Matific/broken-down-models',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
