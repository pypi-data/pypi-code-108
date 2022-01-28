# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spatial_kde']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.8.0,<2.0.0',
 'geopandas>=0.10.2,<0.11.0',
 'numpy>=1.22.1,<2.0.0',
 'pandarallel>=1.5.4,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'pyproj>=3.3.0,<4.0.0',
 'rasterio>=1.2.10,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['skde = spatial_kde.cli:app']}

setup_kwargs = {
    'name': 'spatial-kde',
    'version': '0.1.0',
    'description': 'Create Spatial Kernel Density / Heatmap (as a numpy array or raster) from point based vector data',
    'long_description': '# Spatial Kernel Density Esimation\nCreate Spatial Kernel Density / Heatmap raster from point based vector data, à la QGIS / ArcGIS.\n\n![Example showing KDE generated from weighted points](example.png)\n\nCreates a kernel density (heatmap) raster from vector point data using kernel density estimation. The density is calculated based on the number of points in a location, with larger numbers of clustered points resulting in larger values, and points can be optionally weighted. Kernel Density / Heatmaps allow easy for identification of hotspots and clustering of points. This implementation provides an equivalent to [QGIS\' Heatmap](https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/interpolation.html#heatmap-kernel-density-estimation) and [ArcGIS/ArcMap/ArcPro\'s Kernel Density spatial analyst](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/kernel-density.htm) function. Note that any distance calculations are planar, therefore care should be taken when using points over large areas that are in a geographic coordinate system.\n\nThe implementation of Kernel Density here uses the Quartic kernel for it\'s estimates, with the methodology equivialent to the ArcGIS documentation explaining how [Kernel Density](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/how-kernel-density-works.htm) works. There are many alternative KDE functions available in python that may offer better performance, for example [scipy](https://docs.scipy.org/doc/scipy/reference/stats.html#univariate-and-multivariate-kernel-density-estimation), [scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KernelDensity.html), [KDEpy](https://kdepy.readthedocs.io/en/latest/index.html), though these alternatives may not perform KDE in the same manner as GIS software (namely the Quartic kernel with optional weights).\n\n## Installation\n\n## Usage\n\nAfter installation, the `skde` tool is available from the command line with the following usage:\n\n```shell\nUsage: skde [OPTIONS] VECTOR OUTPUT\n\n  Create a Spatial Kernel Density / Heatmap raster from an input vector.\n\n  The input vector file must be readable by GeoPandas and contain Point type\n  geometry (for non-point geometries the centroid will be used for the KDE).\n\nArguments:\n  VECTOR  Path to input vector file  [required]\n  OUTPUT  Output path for created raster  [required]\n\nOptions:\n  --radius FLOAT                  Radius/Bandwith for the KDE. Same units as\n                                  the CRS of `vector`.  [default: 1]\n  --output-pixel-size FLOAT       Output pixel size (resolution). Same units\n                                  as the CRS of `vector`.  [default: 1]\n  --output-driver TEXT            Output driver (file format) used by rasterio\n                                  (Default = GeoTiff).  [default: GTiff]\n  --weight-field TEXT             Optional field in `vector` containing\n                                  weights of each point.\n  --scaled / --no-scaled          Set to True to scale the KDE values, leave\n                                  false to use raw values.  [default: no-\n                                  scaled]\n```\n\nAlternatively, the [`spatial_kernel_density`](spatial_kde/kde.py) function can be used in python:\n\n```python\nfrom typing import Optional\n\nimport geopandas as gpd\nfrom spatial_kde import spatial_kernel_density\n\n\nspatial_kernel_density(\n    points: gpd.GeoDataFrame = gdf,\n    radius: float = 1.0,\n    output_path: str = "/output/path.tif",\n    output_pixel_size: float = 1.0,\n    output_driver: str = "GTiff",\n    weight_col: Optional[str] = None,\n    scaled: bool = False,\n)\n\n    """Calculate Kernel Density / heatmap from ``points``\n\n    .. note:: Distance calculations are planar so care should be taken with data\n              that is in geographic coordinate systems\n\n    Parameters\n    ----------\n    points : gpd.GeoDataFrame\n        Input GeoDataFrame of points to generate a KDE from\n    radius : float\n        Radius of KDE, same units as the coordinate reference system of ``points``\n        Sometimes referred to as search radius or bandwidth\n    output_path : str\n        Path to write output raster to\n    output_pixel_size : float\n        Output cell/pixel size of the created array. Same units as the coordinate\n        reference system of ``points``\n    output_driver : str\n        Output format (driver) used to create image. See also\n        https://rasterio.readthedocs.io/en/latest/api/rasterio.drivers.html\n    weight_col : Optional[str], optional\n        A column in ``points`` to weight the kernel density by, any points that\n        are NaN in this field will not contribute to the KDE.\n        If None, the all points will have uniform weight of 1.\n    scaled : bool\n        If True will output mathematically scaled values, else will output raw\n        values.\n    """\n```\n\n## Development\n\nPrequisites:\n\n* [poetry](https://python-poetry.org/)\n* [pre-commit](https://pre-commit.com/)\n\nThe Makefile includes helpful commands setting a development environment, get started by installing the package into a new environment and setting up pre-commit by running `make install`. Run `make help` to see additional available commands (e.g. linting, testing and so on).\n\n* [Pytest](https://docs.pytest.org/en/6.2.x/) is used for testing the application (see `/tests`).\n* Code is linted using [flake8](https://flake8.pycqa.org/en/latest/)\n* Code formatting is validated using [Black](https://github.com/psf/black)\n* [pre-commit](https://pre-commit.com/) is used to run these checks locally before files are pushed to git\n* The [Github Actions pipeline](.github/workflows/pipeline.yml) runs these checks and tests\n\n## TODO\n\n- [ ] Github actions pipeline runs on a matrix of python versions\n- [ ] Documentation (e.g. mkdocs, read-the-docs w/ sphinx or similar)\n- [ ] Tooling for managing versioning/releasing (e.g. bump2version)\n- [x] Makefile commands for releasing to (test) pypi\n- [ ] Support geodesic distance calculation',
    'author': 'mblackgeo',
    'author_email': '18327836+mblackgeo@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mblackgeo/spatial-kde',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
