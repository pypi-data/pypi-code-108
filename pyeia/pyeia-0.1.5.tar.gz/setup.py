# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eia', 'eia.api']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'dynaconf>=3.0.0,<4.0.0',
 'httpx>=0.13.3,<0.14.0',
 'loguru>=0.5.1,<0.6.0',
 'pandas>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'pyeia',
    'version': '0.1.5',
    'description': 'Python client for the Energy Information Administration (EIA) API',
    'long_description': '# Configuration\n\nYou can configure pyeia with your API key either at runtime.\n\n- Declare `EIA_APIKEY="myapikey"` in a `.env` file\n- Set an environment variable explicitly, `export EIA_APIKEY="myapikey"`\n- If you are using dynaconf, you can include an `[eia]` environment in your `settings.toml` file (or any other configured settings files.)\n\n```toml\n[eia]\napikey = "my apikey"\n```\n\n# About\n\nThe U.S. Energy Information Adminsitration provides an API for access to commonly used datasets for policy makers\nand researchers. See the [EIA API documentation](http://www.eia.gov/opendata/commands.cfm) for more information.\n\nWarning : This package is a work in progress!  A substantial update is expected in January 2020, with a published version on PyPi.  The author took a break from this domain area, but is returning!  Hoping to have a similar or identical R interface/API as well, but that may be much farther down the pipeline.\n\n# Basic Usage\n\nSince this package is still under active development, it has not been pushed to PyPi. That said, I believe it is\nstable and reliable enough for immediate use.  You can install this via git+https, i.e. :\n\n```bash\npip install pyeia\npip show pyeia\n```\n\nThere are two main strategies for interacting with this package.\n\n## EIA Browser\n\n[EIA provides a web-based data browser](http://www.eia.gov/opendata/qb.cfm)\nSince most interactions for discovering data via the API will likely occur\nthrough this browser, this motivated a programmatic version.\n\nThe general strategy is to traverse a datapath or multiple datapaths, and\nwhen you arrive to the desired node, you flag one or more dataseries.  \nThere is also the ability to add in meta information as you flag a dataseries.\n\nRunning the `export` method on a Browser object will make a request to the\n`Series` API to collect data you\'ve flagged.\n\nThere\'s currently a separate class for each dataset which is mostly syntactic.\nIn the future, there will likely be methods and visualizations builtin that are\nspecific to the datasets described at the root category level from EIA.\n\n1. [Browser Quickstart to Collect AEO data](examples/aeo_quickstart.py)\n2. [Computing Marginal Values for AEO data](examples/aeo_marginal_values.py)\n\n## Direct API usage\n\nEach endpoint has a corresponding class in `eia.api`.  Every class has a `query` method that makes a call to EIA.\nThe returned result is always the response body.  Metadata about the request is dropped.  The `Series` and `Geoset`\nclasses have a special `query_df` method since their response bodies have a naturally tabular schema.\n\n\n```python\nfrom eia import api\n\nmyapikey = ""  # Register here : www.eia.gov/opendata/register.cfm\n\n# Make a call to the Category endpoint\ncategory = api.Category(myapikey)\ncategory.query()\n\n# Make a call to the Series endpoint\nseries = api.Series(\n    "AEO.2015.REF2015.CNSM_DEU_TOTD_NA_DEU_NA_ENC_QBTU.A",\n    "AEO.2015.REF2015.CNSM_ENU_ALLS_NA_DFO_DELV_ENC_QBTU.A",\n    api_key=myapikey,\n)\nseries.to_dict()  # Export data from its json response\n# Make the same query, but get results as a pandas DataFrame\nseries.to_dataframe()\n\n# Make a call to the Geoset endpoint\ngeoset = api.Geoset("ELEC.GEN.ALL-99.A", "USA-CA", "USA-FL", "USA-MN", api_key=myapikey)\ngeoset.to_dict()\ngeoset.query_df()\n\n# Make a call to the SeriesCategory endpoint\n\nseriescategory = api.SeriesCategory(\n    "AEO.2015.REF2015.CNSM_DEU_TOTD_NA_DEU_NA_ENC_QBTU.A",\n    "AEO.2015.REF2015.CNSM_ENU_ALLS_NA_DFO_DELV_ENC_QBTU.A",\n    api_key=myapikey,\n)\nseriescategory.to_dict()\n\n# Make a call to the Updates endpoint\n\nupdates = api.Updates(\n    category_id=2102358,\n    rows=0,\n    firstrow="currently_not_used",\n    deep=False,\n    api_key=myapikey,\n)\nupdates.to_dict()\n\n# Make a call to the Search endpoint\nsearch = api.Search(api_key=myapikey)\n\n# Make a series_id search\nsearch.to_dict("series_id", "EMI_CO2_COMM_NA_CL_NA_NA_MILLMETNCO2.A", "all")\n\n# Make a name search\nsearch.to_dict("name", "crude oil", 25)\n\n# Make a date-range search\n# Dates can be input as a list/tuple of any valid pd.to_datetime argument\nsearch.to_dict("last_updated", ["Dec. 1st, 2014", "06/14/2015 3:45PM"])\n```\n',
    'author': 'Thomas Tu',
    'author_email': 'thomasthetu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thomastu/pyEIA',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
