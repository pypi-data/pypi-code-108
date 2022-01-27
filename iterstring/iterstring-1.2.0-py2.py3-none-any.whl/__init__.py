"""
Simple class that allows writing lists and dicts as heredoc strings

* Write lists as strings with one line per element
* Same for dictionaries, but use first token on each line as key

Features
--------

* Handles comments (using # characters)
* Strips away extraneous whitespace with reasonable defaults (configurable)
* Coerce items to numbers where possible (see coerce)
* Iterating over the object treats it like a list
* Indexing the object treats it like a dictionary
* listr and distr helper functions provide simple interfaces

Examples
--------

A simple use case:

.. code-block:: python

  >>> from iterstring import listr # or distr
  >>> some_list = listr('''
  item one # with a comment
    2
  three
  ''')
  >>> some_list
  ['item one', 2, 'three']
  >>> type(some_list)
  <class 'list'>

Using the class directly:

.. code-block:: python

  >>> from iterstring import Istr
  >>> asdf = Istr('''
  item one # with a comment
    2
  three
  ''')
  >>> asdf.to_list()
  ['item one', 2, 'three']
  >>> type(asdf)
  <class 'iterstring.Istr'>

  >>> [x for x in asdf]
  ['item one', 2, 'three']

  >>> fdsa = Istr('''
  item one # with a comment
    2 some other value
  key3 3.14159
  ''')
  >>> asdf.to_dict()
  {'item': 'one', 2: 'some other value', 'key3': 3.14159}
  >>> asdf.to_dict(coerce=False)
  {'item': 'one', '2': 'some other value', 'key3': '3.14159'}

License
-------

* Free software: MIT license

Documentation
-------------

* https://iterstring.readthedocs.io/
"""

__author__ = """Brendan Strejcek"""
__email__ = 'brendan@datagazing.com'
__version__ = '1.2.0'

from .iterstring import Istr, listr, distr, tlist # noqa F401
