# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stackstac']

package_data = \
{'': ['*']}

install_requires = \
['dask[array]>=2021.4.1,<2023',
 'pyproj>=3.0.0,<4.0.0',
 'rasterio>=1.2.3,<2.0.0',
 'xarray>=0.18,<1']

extras_require = \
{'binder': ['Bottleneck>=1.3.2,<2.0.0',
            'coiled>=0,<1',
            'distributed>=2021.4.1,<2023',
            'geogif>=0,<1',
            'ipyleaflet>=0.13.6,<0.14.0',
            'ipywidgets>=7.6.3,<8.0.0',
            'jupyter-server-proxy>=3.2.0,<4.0.0',
            'jupyterlab-geojson>=3.1.2,<4.0.0',
            'jupyterlab-system-monitor>=0.8.0,<0.9.0',
            'matplotlib>=3.4.1,<4.0.0',
            'planetary-computer>=0.4.3,<1',
            'pystac-client>=0.3,<0.4',
            'sat-search>=0.3.0,<0.4.0'],
 'docs': ['Sphinx>=3.5.4,<4.0.0',
          'furo>=2021.4.11-beta.34,<2022.0.0',
          'ipyleaflet>=0.13.6,<0.14.0',
          'ipython>=7.20.0,<8.0.0',
          'jupyter-sphinx>=0.3.2,<0.4.0',
          'nbsphinx>=0.8.2,<0.9.0',
          'numpydoc>=1.1.0,<2.0.0',
          'pandoc>=1.0.2,<2.0.0',
          'sphinx-autodoc-typehints>=1.11.1,<2.0.0'],
 'viz': ['Pillow>=9.0.0,<10.0.0',
         'aiohttp>=3.7.4,<4.0.0',
         'cachetools>=4.2.2,<5.0.0',
         'distributed>=2021.4.1,<2023',
         'ipyleaflet>=0.13.6,<0.14.0',
         'jupyter-server-proxy>=3.2.0,<4.0.0',
         'matplotlib>=3.4.1,<4.0.0',
         'mercantile>=1.1.6,<2.0.0',
         'scipy>=1.6.1,<2.0.0']}

setup_kwargs = {
    'name': 'stackstac',
    'version': '0.3.1',
    'description': 'Load a STAC collection into xarray with dask',
    'long_description': '# StackSTAC\n\n[![Documentation Status](https://readthedocs.org/projects/stackstac/badge/?version=latest)](https://stackstac.readthedocs.io/en/latest/?badge=latest) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/gjoseph92/stackstac/main?labpath=%2Fdocs%2Fbasic.ipynb%3Ffile-browser-path%3D%2Fexamples)\n\nTurn a list of [STAC](http://stacspec.org) items into a 4D [xarray](http://xarray.pydata.org/en/stable/) DataArray (dims: `time, band, y, x`), including reprojection to a common grid. The array is a lazy [Dask array](https://docs.dask.org/en/latest/array.html), so loading and processing the data in parallel—locally or [on a cluster](https://coiled.io/)—is just a `compute()` call away.\n\nFor more information and examples, please [see the documentation](https://stackstac.readthedocs.io).\n\n```python\nimport stackstac\nimport pystac_client\n\nURL = "https://earth-search.aws.element84.com/v0"\ncatalog = pystac_client.Client.open(URL)\n\nstac_items = catalog.search(\n    intersects=dict(type="Point", coordinates=[-105.78, 35.79]),\n    collections=["sentinel-s2-l2a-cogs"],\n    datetime="2020-04-01/2020-05-01"\n).get_all_items()\n\nstack = stackstac.stack(stac_items)\nprint(stack)\n```\n```\n<xarray.DataArray \'stackstac-fefccf3d6b2f9922dc658c114e79865b\' (time: 13, band: 17, y: 10980, x: 10980)>\ndask.array<fetch_raster_window, shape=(13, 17, 10980, 10980), dtype=float64, chunksize=(1, 1, 1024, 1024), chunktype=numpy.ndarray>\nCoordinates: (12/24)\n  * time                        (time) datetime64[ns] 2020-04-01T18:04:04 ......\n    id                          (time) <U24 \'S2B_13SDV_20200401_0_L2A\' ... \'S...\n  * band                        (band) <U8 \'overview\' \'visual\' ... \'WVP\' \'SCL\'\n  * x                           (x) float64 4e+05 4e+05 ... 5.097e+05 5.098e+05\n  * y                           (y) float64 4e+06 4e+06 ... 3.89e+06 3.89e+06\n    view:off_nadir              int64 0\n    ...                          ...\n    instruments                 <U3 \'msi\'\n    created                     (time) <U24 \'2020-09-05T06:23:47.836Z\' ... \'2...\n    sentinel:sequence           <U1 \'0\'\n    sentinel:grid_square        <U2 \'DV\'\n    title                       (band) object None ... \'Scene Classification ...\n    epsg                        int64 32613\nAttributes:\n    spec:        RasterSpec(epsg=32613, bounds=(399960.0, 3890220.0, 509760.0...\n    crs:         epsg:32613\n    transform:   | 10.00, 0.00, 399960.00|\\n| 0.00,-10.00, 4000020.00|\\n| 0.0...\n    resolution:  10.0\n```\n\nOnce in xarray form, many operations become easy. For example, we can compute a low-cloud weekly mean-NDVI timeseries:\n\n```python\nlowcloud = stack[stack["eo:cloud_cover"] < 40]\nnir, red = lowcloud.sel(band="B08"), lowcloud.sel(band="B04")\nndvi = (nir - red) / (nir + red)\nweekly_ndvi = ndvi.resample(time="1w").mean(dim=("time", "x", "y")).rename("NDVI")\n# Call `weekly_ndvi.compute()` to process ~25GiB of raster data in parallel. Might want a dask cluster for that!\n```\n\n## Installation\n\n```\npip install stackstac\n```\n\nWindows notes:\n\nIt\'s a good idea to use `conda` to handle installing rasterio on Windows. There\'s considerably more pain involved with GDAL-type installations using pip. Then `pip install stackstac`.\n\n## Things `stackstac` does for you:\n\n* Figure out the geospatial parameters from the STAC metadata (if possible): a coordinate reference system, resolution, and bounding box.\n* Transfer the STAC metadata into [xarray coordinates](http://xarray.pydata.org/en/stable/data-structures.html#coordinates) for easy indexing, filtering, and provenance of metadata.\n* Efficiently generate a Dask graph for loading the data in parallel.\n* Mediate between Dask\'s parallelism and GDAL\'s aversion to it, allowing for fast, multi-threaded reads when possible, and at least preventing segfaults when not.\n* Mask nodata and rescale by dataset-level scales/offsets.\n* Display data in interactive maps in a notebook, computed on the fly by Dask.\n\n## Limitations:\n\n* **Raster data only!** We are currently ignoring other types of assets you might find in a STAC (XML/JSON metadata, point clouds, video, etc.).\n* **Single-band raster data only!** Each band has to be a separate STAC asset—a separate `red`, `green`, and `blue` asset on each Item is great, but a single `RGB` asset containing a 3-band GeoTIFF is not supported yet.\n* [COG](https://www.cogeo.org)s work best. "Normal" GeoTIFFs that aren\'t internally tiled, or don\'t have overviews, will see much worse performance. Sidecar files (like `.msk` files) are ignored for performance. JPEG2000 will probably work, but probably be slow unless you buy kakadu. [Formats make a big difference](https://medium.com/@_VincentS_/do-you-really-want-people-using-your-data-ec94cd94dc3f).\n* BYOBlocksize. STAC doesn\'t offer any metadata about the internal tiling scheme of the data. Knowing it can make IO more efficient, but actually reading the data to figure it out is slow. So it\'s on you to set this parameter. (But if you don\'t, things should be fine for any reasonable COG.)\n* Doesn\'t make geospatial data any easier to work with in xarray. Common operations (picking bands, clipping to bounds, etc.) are tedious to type out. Real geospatial operations (shapestats on a GeoDataFrame, reprojection, etc.) aren\'t supported at all. [rioxarray](https://corteva.github.io/rioxarray/stable/readme.html) might help with some of these, but it has limited support for Dask, so be careful you don\'t kick off a huge computation accidentally.\n* I haven\'t even written tests yet! Don\'t use this in production. Or do, I guess. Up to you.\n\n## Roadmap:\n\nShort-term:\n\n- Write tests and add CI (including typechecking)\n- Support multi-band assets\n- Easier access to `s3://`-style URIs (right now, you\'ll need to pass in `gdal_env=stackstac.DEFAULT_GDAL_ENV.updated(always=dict(session=rio.session.AWSSession(...)))`)\n- Utility to guess blocksize (open a few assets)\n- Support [item assets](https://github.com/radiantearth/stac-spec/tree/master/extensions/item-assets) to provide more useful metadata with collections that use it (like S2 on AWS)\n- Rewrite dask graph generation once the [Blockwise IO API](https://github.com/dask/dask/pull/7281) settles\n\nLong term (if anyone uses this thing):\n- Support other readers ([aiocogeo](https://github.com/geospatial-jeff/aiocogeo)?) that may perform better than GDAL for specific formats\n- Interactive mapping with [xarray_leaflet](https://github.com/davidbrochart/xarray_leaflet), made performant with some Dask graph-rewriting tricks to do the initial IO at coarser resolution for lower zoom levels (otherwize zooming out could process terabytes of data)\n- Improve ergonomics of xarray for raster data (in collaboration with [rioxarray](https://corteva.github.io/rioxarray/stable/readme.html))\n- Implement core geospatial routines (warp, vectorize, vector stats, [GeoPandas](https://geopandas.org)/[spatialpandas](https://github.com/holoviz/spatialpandas) interop) in Dask\n',
    'author': 'Gabe Joseph',
    'author_email': 'gjoseph92@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://stackstac.readthedocs.io/en/latest/index.html',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
