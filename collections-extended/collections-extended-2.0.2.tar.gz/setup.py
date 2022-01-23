# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['collections_extended']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'collections-extended',
    'version': '2.0.2',
    'description': 'Extra Python Collections - bags (multisets) and setlists (ordered sets)',
    'long_description': 'README\n######\n\n.. image:: https://coveralls.io/repos/github/mlenzen/collections-extended/badge.svg?branch=master\n\t:target: https://coveralls.io/github/mlenzen/collections-extended?branch=master\n\t:alt: Coverage\n\n\n.. image:: https://pepy.tech/badge/collections-extended/week\n\t:target: https://pepy.tech/project/collections-extended/\n\t:alt: Downloads\n\n\nDocumentation:\n\thttp://collections-extended.lenzm.net/\nGitHub:\n\thttps://github.com/mlenzen/collections-extended\nPyPI:\n\thttps://pypi.python.org/pypi/collections-extended\n\nOverview\n========\n\n``collections_extended`` is a pure Python module with no dependencies providing:\n\n- a ``bag`` class, AKA **multiset**,\n- a ``setlist`` class, which is a **unique list** or **ordered set**,\n- a ``bijection`` class, ``RangeMap`` which is a mapping from ranges to values and\n- a ``IndexedDict`` class, which is an ordered mapping whose elements can be accessed using index, in addition to key.\n\nThere are also frozen (hashable) varieties of bags and setlists.\n\nCompatible with and tested against Python 3.6, 3.7, 3.8, 3.9, 3.10 & PyPy3.\n\nGetting Started\n===============\n\n.. code-block:: python\n\n\t>>> from collections_extended import bag, setlist, bijection, RangeMap, IndexedDict\n\t>>> from datetime import date\n\t>>> b = bag(\'abracadabra\')\n\t>>> b.count(\'a\')\n\t5\n\t>>> b.remove(\'a\')\n\t>>> b.count(\'a\')\n\t4\n\t>>> \'a\' in b\n\tTrue\n\t>>> b.count(\'d\')\n\t1\n\t>>> b.remove(\'d\')\n\t>>> b.count(\'d\')\n\t0\n\t>>> \'d\' in b\n\tFalse\n\n\t>>> sl = setlist(\'abracadabra\')\n\t>>> sl\n\tsetlist((\'a\', \'b\', \'r\', \'c\', \'d\'))\n\t>>> sl[3]\n\t\'c\'\n\t>>> sl[-1]\n\t\'d\'\n\t>>> \'r\' in sl  # testing for inclusion is fast\n\tTrue\n\t>>> sl.index(\'d\')  # so is finding the index of an element\n\t4\n\t>>> sl.insert(1, \'d\')  # inserting an element already in raises a ValueError\n\tTraceback (most recent call last):\n\t...\n\t\traise ValueError\n\tValueError\n\t>>> sl.index(\'d\')\n\t4\n\n\t>>> bij = bijection({\'a\': 1, \'b\': 2, \'c\': 3})\n\t>>> bij.inverse[2]\n\t\'b\'\n\t>>> bij[\'a\'] = 2\n\t>>> bij == bijection({\'a\': 2, \'c\': 3})\n\tTrue\n\t>>> bij.inverse[1] = \'a\'\n\t>>> bij == bijection({\'a\': 1, \'c\': 3})\n\tTrue\n\n\t>>> version = RangeMap()\n\t>>> version[date(2017, 10, 20): date(2017, 10, 27)] = \'0.10.1\'\n\t>>> version[date(2017, 10, 27): date(2018, 2, 14)] = \'1.0.0\'\n\t>>> version[date(2018, 2, 14):] = \'1.0.1\'\n\t>>> version[date(2017, 10, 24)]\n\t\'0.10.1\'\n\t>>> version[date(2018, 7, 1)]\n\t\'1.0.1\'\n\t>>> version[date(2018, 6, 30):] = \'1.0.2\'\n\t>>> version[date(2018, 7, 1)]\n\t\'1.0.2\'\n\n\t>>> idict = IndexedDict()\n\t>>> idict[\'a\'] = "A"\n\t>>> idict[\'b\'] = "B"\n\t>>> idict[\'c\'] = "C"\n\t>>> idict.get(key=\'a\')\n\t\'A\'\n\t>>> idict.get(index=2)\n\t\'C\'\n\t>>> idict.index(\'b\')\n\t1\n\nInstallation\n============\n\n``pip install collections-extended``\n\nUsage\n=====\n\t``from collections_extended import bag, frozenbag, setlist, frozensetlist, bijection``\n\nClasses\n=======\nThere are seven new collections provided:\n\nBags\n----\nbag\n\tThis is a bag AKA multiset.\nfrozenbag\n\tThis is a frozen (hashable) version of a bag.\n\nSetlists\n--------\nsetlist\n\tAn ordered set or a list of unique elements depending on how you look at it.\nfrozensetlist\n\tThis is a frozen (hashable) version of a setlist.\n\nMappings\n--------\nbijection\n\tA one-to-one mapping.\nRangeMap\n\tA mapping from ranges (of numbers/dates/etc)\nIndexedDict\n\tA mapping that keeps insertion order and allows access by index.\n\nPython 2\n--------\n\nThe package no longer supports Python 2. The last version to support\nPython 2.7, 3.4 & 3.5 was 1.0. No new feature releases will be done for 1.x but\nany significant bugs that come up may be fixed.\n\n:Author: Michael Lenzen\n:Copyright: 2021 Michael Lenzen\n:License: Apache License, Version 2.0\n:Project Homepage: https://github.com/mlenzen/collections-extended\n',
    'author': 'Michael Lenzen',
    'author_email': 'm.lenzen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mlenzen/collections-extended',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
