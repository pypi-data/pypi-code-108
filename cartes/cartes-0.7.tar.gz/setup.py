# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cartes',
 'cartes.atlas',
 'cartes.crs',
 'cartes.dataviz',
 'cartes.dataviz.markers',
 'cartes.osm',
 'cartes.osm.overpass',
 'cartes.osm.overpass.relations',
 'cartes.tests',
 'cartes.utils']

package_data = \
{'': ['*'], 'cartes.tests': ['cache/*']}

install_requires = \
['Cartopy>=0.19',
 'Shapely>=1.8.0,<2.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'altair>=4.2.0,<5.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'bs4>=0.0.1,<0.0.2',
 'geopandas>=0.10.2,<0.11.0',
 'importlib-metadata>=4.2,<5.0',
 'jsonschema>=3.0,<4.0',
 'lxml>=4.7.1,<5.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21',
 'pandas>=1.3.5,<2.0.0',
 'pyproj>=3.1.0',
 'requests>=2.27.1,<3.0.0',
 'scipy>=1.7.3,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['cartes = cartes.__main__:main']}

setup_kwargs = {
    'name': 'cartes',
    'version': '0.7',
    'description': 'A generic toolbox for building maps in Python',
    'long_description': '# Cartes\n\n![build](https://github.com/xoolive/cartes/workflows/build/badge.svg)\n![docs](https://github.com/xoolive/cartes/actions/workflows/github-pages.yml/badge.svg)\n[![Code Coverage](https://img.shields.io/codecov/c/github/xoolive/cartes.svg)](https://codecov.io/gh/xoolive/cartes)\n[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy.readthedocs.io/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n![License](https://img.shields.io/pypi/l/cartes.svg)\\\n![PyPI version](https://img.shields.io/pypi/v/cartes)\n[![PyPI downloads](https://img.shields.io/pypi/dm/cartes)](https://pypi.org/project/cartes)\n![Conda version](https://img.shields.io/conda/vn/conda-forge/cartes)\n[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/cartes.svg)](https://anaconda.org/conda-forge/cartes)\n\nCartes is a Python library providing facilities to produce meaningful maps.\n\nCartes builds on top of most common Python visualisation libraries (Matplotlib/Cartopy, Altair, ipyleaflet) and data manipulation libraries (Pandas, Geopandas) and provides mostly:\n\n- a **comprehensive set of geographic projections**, built on top of Cartopy and Altair/d3.js;\n- an **interface to OpenstreetMap Nominatim and Overpass API**. Result of requests are parsed in a convenient format for preprocessing and storing in standard formats;\n- beautiful **default parameters** for quality visualisations;\n- **advanced caching facilities**. Do not download twice the same content in the same day.\n\nThe cartes library is a powerful asset to **publish clean, lightweight geographical datasets**; and to **produce decent geographical visualisations** in few lines of code.\n\n## Gallery\n\n<a href="https://cartes-viz.github.io/gallery/mercantour.html"><img width="20%" src="https://cartes-viz.github.io/_static/homepage/mercantour.png"></a>\n<a href="https://cartes-viz.github.io/gallery/footprint.html"><img width="20%" src="https://cartes-viz.github.io/_static/homepage/antibes.png"></a>\n<a href="https://cartes-viz.github.io/gallery/airports.html"><img width="20%" src="https://cartes-viz.github.io/_static/homepage/airports.png"></a>\n<a href="https://cartes-viz.github.io/gallery/tokyo_metro.html#zoom-in-to-downtown-tokyo"><img width="20%" src="https://cartes-viz.github.io/_static/homepage/tokyo.png"></a>\n\nMore in the [documentation](https://cartes-viz.github.io/gallery.html)\n\n## Installation\n\nLatest release:\n\nRecommended, with conda:\n```sh \nconda install -c conda-forge cartes\n```\n\nor with pip:\n```sh\npip install cartes\n```\n\nDevelopment version:\n\n```sh\ngit clone https://github.com/xoolive/cartes\ncd cartes\npip install .\n```\n\n## Documentation\n\n![docs](https://github.com/xoolive/cartes/actions/workflows/github-pages.yml/badge.svg)\n\nDocumentation available at https://cartes-viz.github.io/\n',
    'author': 'Xavier Olive',
    'author_email': 'git@xoolive.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
