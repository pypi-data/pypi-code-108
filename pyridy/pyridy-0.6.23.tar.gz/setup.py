# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyridy',
 'pyridy.osm',
 'pyridy.osm.utils',
 'pyridy.processing',
 'pyridy.utils']

package_data = \
{'': ['*']}

install_requires = \
['HeapDict>=1.0.1,<2.0.0',
 'Sphinx>=4.2.0,<5.0.0',
 'geopy>=2.1.0,<3.0.0',
 'ipyleaflet>=0.15.0,<0.16.0',
 'matplotlib>=3.4.1,<4.0.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.21.5,<2.0.0',
 'overpy>=0.6,<0.7',
 'pandas>=1.2.4,<2.0.0',
 'pyproj>=3.3.0,<4.0.0',
 'pytest>=6.2.3,<7.0.0',
 'requests>=2.25.1,<3.0.0',
 'scipy>=1.6.3,<2.0.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0',
 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'pyridy',
    'version': '0.6.23',
    'description': 'Support library for measurements made with the Ridy Android App',
    'long_description': '# PyRidy\n\n![alt text](assets/ic_launcher.png "PyRidy Logo")\n\nPython Support Library to import and process Ridy files\n\n### About Ridy\nRidy is an Android App to record sensor data for uses in science and engineering. The app is currently actively being \ndeveloped at the [Chair and Institute for Rail Vehicles and Transport Systems (IFS)](http://www.ifs.rwth-aachen.de/en/start/)\n\n<img src="assets/screenshot.png" alt="Ridy Screenshot" width="200"/>\n\nAt the institute Ridy is e.g. used for condition monitoring of railway tracks and several more use-cases are currently\nresearched upon.\nAmong other, Ridy can record:\n* Acceleration\n* Linear Acceleration (i.e., without g-Force)\n* Magnetic Field\n* Gyroscope\n* Orientation\n* GNSS Location (+ Android Raw GNSS Measurements)\n* Pressure, Humidity, Temperature, Ambient Light\n\nCompared to other existing apps Ridy can perform long measurements even in the background when the phone is locked.\nThe app supports two formats for data export, JSON and SQLITE. If you would like to use or try out the app please contact the\ndeveloper (see below) to get access.\n\n### About PyRidy\nPyRidy is the companion python library for the Ridy Android App. It provides easy access to the data no matter which\nrecording format was used. If pyridy is used, one does no longer need to manually write code to import the files.\n\nIn addition, pyridy provides several more features:\n* Automatic conversion of sensor data into objects and numpy arrays\n* Conversion of arrays to Pandas DataFrame objects\n* Time synchronization of individual files (e.g. from different phones)\n* Download of OSM Railway Data via the Overpass API\n* Plotting of GPS tracks onto a map using ipyleaflet\n\n### Documentation\n[PyRidy Documentation](https://pyridy.readthedocs.io/)\n#### Installation\n\nInstall using pip\n```python\n    pip install pyridy\n```\nNote that pyridy depends on geopandas, the best way to install geopandas is usually using conda\n```python\n    conda install geopandas\n```\nSee the [GeoPandas documentation](https://geopandas.org/) for more details.\n\n#### Usage\n\nInformation and examples on how to use the library can be found in the [PyRidy documentation](https://pyridy.readthedocs.io/)\n\n### Developer\nPhilipp Leibner - philipp.leibner@ifs.rwth-aachen.de\n<div>  \n<a href="">\n    <img src="assets/ifs_logo_rgb.svg" alt="IFS Logo" width="400">\n  </a>\n</div>\n',
    'author': 'Philipp Simon Leibner',
    'author_email': 'philipp.leibner@ifs.rwth-aachen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
