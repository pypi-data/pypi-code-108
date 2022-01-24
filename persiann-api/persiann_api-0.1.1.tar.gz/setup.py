# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['persiann_api']

package_data = \
{'': ['*']}

install_requires = \
['GDAL>=3.3.2',
 'Pillow>=9.0.0,<10.0.0',
 'numpy>=1.21.5,<2.0.0',
 'setuptools==57.5.0']

setup_kwargs = {
    'name': 'persiann-api',
    'version': '0.1.1',
    'description': 'Unofficial PERSIANN Python API.',
    'long_description': '# persiann_api\n\nThe __persiann_api__ python package was built in order to make data more readily available for data scientist, analyst, etc, that wish to work with weather data through the [PERSIANN](https://chrsdata.eng.uci.edu/) database. __It is not an official API for the PERSIANN project__.\n\nThe PERSIANN database is made from the "system developed by the Center for Hydrometeorology and Remote Sensing (CHRS) at the University of California, Irvine (UCI) uses neural network function classification/approximation procedures to compute an estimate of rainfall rate at each 0.25° x 0.25° pixel of the infrared brightness temperature image provided by geostationary satellites."\n\nAs our API currently download the data in the GeoTIFF format, every "pixel" in the .tiff file would be the value of the rainfall rate at the 0.25° x 0.25° space.\n\n![PERSIANN data. Screenshot taken from https://chrsdata.eng.uci.edu/ .](github_images/PERSIANN_example.png)\n\nThe screenshot above was taken from https://chrsdata.eng.uci.edu/, which is the official site for the PERSIANN project. This was taken from Brazil in the 28th of December!\n\n# Installation\n\nInstall it throught pip or [Poetry](https://python-poetry.org/), if you already have the [gdal](https://pypi.org/project/GDAL/) package.\n\n```bash\npip install persiann_api\n```\n```bash\npoetry add persiann_api\n```\n\nThe *gdal* package is not so easy to straightforward install. Click in this link for the official guide in PyPi, click [here](https://pypi.org/project/GDAL/). \n\nThere is also this guide for Ubuntu users, click [here](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html). This is the summary for Ubuntu users:\n\n```bash\n\nsudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update\nsudo apt-get update\nsudo apt-get install gdal-bin\n\nogrinfo --version\n```\n\nThen, install the specific version of GDAL from the previous output.\n\n```bash\nsudo apt-get install libgdal-dev\nexport CPLUS_INCLUDE_PATH=/usr/include/gdal\nexport C_INCLUDE_PATH=/usr/include/gdal\n\npip install GDAL==[SPECIFIC VERSION FROM THE \'ogrinfo\' OUTPUT]\n```\n\n# Usage\n\nThe API has one main function that downloads the data inside a folder given some parameters.\n\n```python\nfrom persiann_api.main import download_data\nfrom PIL import Image\n\n# downloads daily data and store each data from date inside the folder.\ndownload_data(\n    from_date=datetime.date(2021, 12, 28),\n    to_date=datetime.date(2021, 12, 28),\n    folder=\'data/\',\n    # bounding box for Brazil\n    lat_bb=(-35, 6),\n    lon_bb=(-69, -36)\n)\n# read the GeoTIFF with your favorite package\ngeotiff_path = \'data/2021_12_28.tiff\'\narr = np.asarray(Image.open(geotiff_path, mode=\'r\'))[::-1] # we must mirror the array for the GeoTIFF.\nplt.imshow(arr)\nplt.clim(0, 78)\n```\n\n![PERSIANN data for Brazil from 28st December of 2021.](github_images/PERSIANN_API_example.png)\n\nSee? This is the same data as the first original data!\n\nThis is a longer example to put here, but in the [notebooks](notebooks/testing_persiann_api.ipynb) folder you can find the code to generate this picture:\n\n![PERSIANN data for Brazil from 28st December of 2021.](github_images/PERSIANN_API_example_geopandas_georasters.png)',
    'author': 'martins6',
    'author_email': 'adrielfalcao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Martins6/persiann_api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
