# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyraptor', 'pyraptor.dao', 'pyraptor.gtfs', 'pyraptor.model']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.0.1,<2.0.0', 'loguru>=0.5.3,<0.6.0', 'pandas>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'pyraptor',
    'version': '0.3.0',
    'description': 'Journey planner with RAPTOR algorithm',
    'long_description': '# PyRaptor\n\nPython implementation of RAPTOR using GTFS data.\n\nThree applications:\n\n- `pyraptor/gtfs/timetable.py` - Extract the time table information for one operator from a GTFS dataset and write it to an optimized format for querying with RAPTOR.\n- `pyraptor/query.py` - Get the best journey for a given origin, destination and desired departure time using RAPTOR\n- `pyraptor/range_query.py` - Get a list of the best journeys to all destinations for a given origin and desired departure time window using RAPTOR\n\n## Installation\n\nInstall from PyPi using `pip install pyraptor` or clone this repository and install from source using pip.\n\n## Example usage\n\n### 1. Create timetable from GTFS\n\n`python pyraptor/gtfs/timetable.py -d "20211201" -a NS`\n\n### 2. Run (range) queries on timetable\n\n`python pyraptor/query.py -i output/optimized_timetable -or "Arnhem Zuid" -d "Oosterbeek" -t "08:30:00"`\n\n`python pyraptor/range_query.py -i output/optimized_timetable -or "Arnhem Zuid" -d "Oosterbeek" -st "08:00:00" -et "08:30:00"`\n\n# References\n\n[Round-Based Public Transit Routing](https://www.microsoft.com/en-us/research/wp-content/uploads/2012/01/raptor_alenex.pdf), Microsoft.com, Daniel Delling et al\n\n[Raptor, another journey planning algorithm](https://ljn.io/posts/raptor-journey-planning-algorithm), Linus Norton\n\n[Dutch GTFS feed](http://transitfeeds.com/p/ov/814), Transit Feeds\n',
    'author': 'Leo van der Meulen, Thom Hopmans',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lmeulen/pyraptor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
