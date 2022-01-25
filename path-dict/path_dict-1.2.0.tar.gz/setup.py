# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['path_dict']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'path-dict',
    'version': '1.2.0',
    'description': 'The versatile dict for Python!',
    'long_description': '# PathDict\n\n[![Downloads](https://pepy.tech/badge/path-dict)](https://pepy.tech/project/path-dict)\n[![Downloads](https://pepy.tech/badge/path-dict/month)](https://pepy.tech/project/path-dict)\n[![Downloads](https://pepy.tech/badge/path-dict/week)](https://pepy.tech/project/path-dict)\n\n\nThe versatile dict for Python!\n\n\n## Installation\n`pip3 install path-dict`\n\nImport:\n\n```python\nfrom path_dict import PathDict\n```\n\n\n\n## Usage\nPathDict is like a normal python dict, but comes with some handy extras.\n\n\n\n### Initialize\n\n```python\n# Empty PathDict\npd = PathDict()\n\n> pd\n---> PathDict({})\n\n```\n\nA PathDict keeps a reference to the original initializing dict:\n\n```python\nuser = {\n\t"name": "Joe",\n\t"age": 22,\n\t"hobbies": ["Playing football", "Podcasts"]\n\t"friends": {\n\t\t"Sue": {"age": 30},\n\t\t"Ben": {"age": 35},\n\t}\n}\njoe = PathDict(user)\n> joe == user\n---> True\n> joe.dict is user\n---> True\n```\n\nYou can also get a deep copy:\n\n```python\njoe = PathDict(user, deepcopy=True)\n> joe == user\n---> True\n> joe.dict is user\n---> False\n```\n\n\n\n### Getting and setting values with paths\n\nYou can use paths of keys to access values:\n\n```python\njoe = PathDict(user, deepcopy=True)\n\n# Get existing path\n> joe["friends", "Sue", "age"]\n---> 30\n\n# Get non-existent, but valid path\n> joe["friends", "Josef", "age"]\n---> None\n\n# Set non-existent, but valid path, creates keys\njoe["authentification", "password"] = "abc123"\n> joe["authentification"]\n---> PathDict({"password": "abc123"})\n```\n\nUsing invalid paths to get or set a value will result in an error. An invalid path is a path that tries to access a key of an int or list, for example. So, only use paths to access hierarchies of PathDicts.\n\n\n```python\njoe = PathDict(user, deepcopy=True)\n\n# Get invalid path (joe["hobbies"] is a list)\n> joe["hobbies", "not_existent"]\n---> Error!\n```\n\n\n\n### Most dict methods are supported\n\nMany of the usual dict methods work with PathDict:\n\n```python\npathdict = ...\n\nfor key, value in pathdict.items():\n\t...\n\nfor key in pathdict:\n\t...\n\nfor key in pathdict.keys():\n\t...\n\nfor value in pathdict.values():\n\t...\n\n```\n\n\n### Apply a function at a path\n\nWhen setting a value, you can use a lambda function to modify the value at a given path.\nThe function should take one argument and return the modified value.\n\n\n```python\nstats_dict = {}\nstats_pd = PathDict({})\n\n# Using a standard dict:\nif "views" not in stats_dict:\n\tstats_dict["views"] = {}\nif "total" not in stats_dict["views"]:\n\t stats_dict["views"]["total"] = 0\nstats_dict["views"]["total"] += 1\n\n# You can achieve the same using a PathDict:\nstats_pd["views", "total"] = lambda x: (x or 0) + 1\n```\n\n\n\n### Filtering\n\nPathDicts offer a filter function, which can filter a list or a PathDict at a given path in-place.\n\nTo filter a list, pass a function that takes one argument (eg. `lambda ele: return ele > 10`) and returns True if the value should be kept, else False.\nTo filter a PathDict, pass a function that takes two arguments (eg. `lambda key, value: key != "1"`) and returns True if the key-value pair should be kept, else False.\n\nYou can filter the PathDict filter is called on, or you can also pass a path into the filter to apply the filter at a given path.\n\nA filtered function is also offered, which does the same, but returns a filtered deepcopy instead of filtering in-place.\n\n\n```python\njoe = PathDict(user, deepcopy=True)\n\n# Remove all friends that are older than 33.\njoe.filter("friends", f=lambda k, v: v["age"] < 33)\n\n> joe["friends"]\n---> PathDict({\n\t"Sue": {"age": 30}\n})\n```\n\n\n### Aggregating\n\nThe aggregate function can combine a PathDict to a single aggregated value.\nIt takes an init parameter, and a function with takes three arguments (eg. `lambda key, val, agg`)\n\n```python\njoe = PathDict(user, deepcopy=True)\n\n# Remove all friends that are older than 33.\nfriend_ages = joe.aggregate("friends", init=0, f=lambda k, v, a: a + v["age"])\n\n> friend_ages\n---> 65\n```\n\n### Serialize to JSON\n\nTo serialize a PathDict to JSON, call `json.dumps(path_dict.dict)`.\nIf you try to serialize a PathDict object itself, the operation will fail.\n',
    'author': 'Marcel Kröker',
    'author_email': 'kroeker.marcel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mkrd/PathDict',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
