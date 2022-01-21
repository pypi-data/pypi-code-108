# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['thinkgisdump']

package_data = \
{'': ['*']}

install_requires = \
['geojson-rewind>=1.0.2,<2.0.0',
 'lxml>=4.7.1,<5.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['thinkgis2geojson = thinkgisdump.cli:main']}

setup_kwargs = {
    'name': 'thinkgisdump',
    'version': '0.2.0b0',
    'description': 'Command line tool for scraping GeoJSON from ThinkGIS sites',
    'long_description': '# thinkgisdump\n\n[![Build status](https://github.com/pjsier/thinkgisdump/workflows/CI/badge.svg)](https://github.com/pjsier/thinkgisdump/actions)\n![pypi](https://img.shields.io/pypi/v/thinkgisdump)\n\nCommand line tool for scraping GeoJSON from [ThinkGIS](https://www.wthgis.com/) sites. Based on [pyesridump](https://github.com/openaddresses/pyesridump).\n\n## Install\n\nYou can install `thinkgisdump` using pip with the following command:\n\n```shell\npip install thinkgisdump\n```\n\nThis will add the script `thinkgis2geojson` to your path.\n\n## Usage\n\n```shell\nusage: thinkgis2geojson [-h] [-l LAYER_ID] [-o OUTPUT] [-q QUIET] url\n\nScrape GeoJSON from ThinkGIS sites\n\npositional arguments:\n  url                   ThinkGIS server URL, layer ID will be parsed from the dsid query param if present\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -l LAYER_ID, --layer-id LAYER_ID\n                        Layer ID (in the dsid query param) to be scraped\n  -o OUTPUT, --output OUTPUT\n                        Output file name, defaults to stdout\n  -q QUIET, --quiet QUIET\n                        Suppress logging of feature requests\n```\n\nBecause of the defaults and setting the layer ID based on query params, the following two command are equivalent.\n\n```shell\nthinkgis2geojson https://richlandil.wthgis.com --layer-id 1283 -o richland-precincts.geojson\nthinkgis2geojson \'https://richlandil.wthgis.com?dsid=1283\' > richland-precincts.geojson\n```\n\n## Notes\n\nTo get the parameters you\'ll need to scrape a given ThinkGIS layer, you can open the "Index" section on a map page. On the map index panel that opens up, you can open developer tools to see the full URL of the link for the layer you\'re interested in. The layer ID will be in the `dsid` parameter. You can also use this full URL including the query parameter in the `url` argument and it will be used without supplying `--layer-id` separately.\n\nThinkGIS returns point and multipoint geometries as polygon circles. When these are encountered, the mean point of the circle is used to create a point or multipoint GeoJSON geometry. Line shapes are also returned as polygons, and currently these are returned as polygons without further transformation.\n',
    'author': 'Pat Sier',
    'author_email': 'pjsier@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pjsier/thinkgisdump',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
