# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wetterdienst',
 'wetterdienst.core',
 'wetterdienst.core.scalar',
 'wetterdienst.metadata',
 'wetterdienst.provider',
 'wetterdienst.provider.dwd',
 'wetterdienst.provider.dwd.forecast',
 'wetterdienst.provider.dwd.forecast.metadata',
 'wetterdienst.provider.dwd.metadata',
 'wetterdienst.provider.dwd.observation',
 'wetterdienst.provider.dwd.observation.metadata',
 'wetterdienst.provider.dwd.observation.util',
 'wetterdienst.provider.dwd.radar',
 'wetterdienst.provider.dwd.radar.metadata',
 'wetterdienst.provider.eccc',
 'wetterdienst.provider.eccc.observation',
 'wetterdienst.provider.eccc.observation.metadata',
 'wetterdienst.provider.eumetnet',
 'wetterdienst.provider.eumetnet.opera',
 'wetterdienst.provider.noaa',
 'wetterdienst.provider.noaa.ghcn',
 'wetterdienst.ui',
 'wetterdienst.ui.explorer',
 'wetterdienst.ui.explorer.layout',
 'wetterdienst.util']

package_data = \
{'': ['*'], 'wetterdienst.ui.explorer': ['assets/*']}

install_requires = \
['Pint>=0.17,<0.18',
 'PyPDF2>=1.26,<2.0',
 'aenum>=3.0,<4.0',
 'aiohttp>=3.7,<4.0',
 'appdirs>=1.4,<2.0',
 'beautifulsoup4>=4.9,<5.0',
 'cachetools>=4.1,<5.0',
 'click-params>=0.1,<0.2',
 'click>=7.1,<8.0',
 'cloup>=0.8,<0.9',
 'dateparser>=1.0,<2.0',
 'deprecation>=2.1,<3.0',
 'dogpile.cache>=1.0,<2.0',
 'fsspec==2021.7',
 'lxml>=4.5,<5.0',
 'measurement>=3.2,<4.0',
 'numpy>=1.19,<2.0',
 'pandas>=1.3,<2.0',
 'python-dateutil>=2.8,<3.0',
 'rapidfuzz>=1.4,<2.0',
 'requests-ftp>=0.3,<0.4',
 'requests>=2.20,<3.0',
 'scipy>=1.5,<2.0',
 'tabulate>=0.8,<0.9',
 'timezonefinder>=5.2,<6.0',
 'tqdm>=4.47,<5.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.7,<2.0'],
 'cratedb': ['crate[sqlalchemy]>=0.25,<0.26'],
 'docs': ['matplotlib>=3.3,<4.0',
          'sphinx>=3.2,<4.0',
          'sphinx-material>=0.0.30,<0.0.31',
          'sphinx-autodoc-typehints>=1.11,<2.0',
          'sphinxcontrib-svg2pdfconverter>=1.1,<2.0',
          'tomlkit>=0.7,<0.8',
          'ipython>=7.10,<8.0'],
 'duckdb': ['duckdb>=0.2,<0.3'],
 'explorer': ['plotly>=4.14,<5.0',
              'dash>=1.19,<2.0',
              'dash-bootstrap-components>=0.12,<0.13'],
 'export': ['openpyxl>=3.0,<4.0', 'sqlalchemy>=1.3,<2.0', 'xarray>=0.17,<0.18'],
 'export:sys_platform != "darwin" or sys_platform == "darwin" and platform_machine != "arm64"': ['pyarrow>=3.0,<4.0',
                                                                                                 'zarr>=2.7,<3.0'],
 'influxdb': ['influxdb>=5.3,<6.0', 'influxdb-client>=1.18,<2.0'],
 'ipython': ['matplotlib>=3.3,<4.0',
             'ipython>=7.10,<8.0',
             'ipython-genutils>=0.2,<0.3'],
 'mpl': ['matplotlib>=3.3,<4.0'],
 'mysql': ['mysqlclient>=2.0,<3.0'],
 'postgresql': ['psycopg2-binary>=2.8,<3.0'],
 'radar': ['wradlib>=1.9,<2.0'],
 'restapi': ['fastapi>=0.61,<0.62', 'uvicorn>=0.13,<0.14'],
 'sql': ['duckdb>=0.2,<0.3']}

entry_points = \
{'console_scripts': ['wddump = wetterdienst.provider.dwd.radar.cli:wddump',
                     'wetterdienst = wetterdienst.ui.cli:cli']}

setup_kwargs = {
    'name': 'wetterdienst',
    'version': '0.24.0',
    'description': 'Open weather data for humans',
    'long_description': 'Wetterdienst - Open weather data for humans\n###########################################\n\n.. container:: align-center\n\n    .. figure:: https://raw.githubusercontent.com/earthobservations/wetterdienst/main/docs/img/german_weather_stations.png\n        :alt: German weather stations managed by Deutscher Wetterdienst\n\n    *“You must be the change you wish to see in the world.” — Gandhi*\n\n    .. figure:: https://raw.githubusercontent.com/earthobservations/wetterdienst/main/docs/img/temperature_ts.png\n        :alt: temperature timeseries of Hohenpeissenberg/Germany\n\n    *"Three things are (almost) infinite: the universe, human stupidity and the temperature time series of\n    Hohenpeissenberg I got with the help of wetterdienst; and I\'m not sure about the universe." - Albert Einstein*\n\n    .. figure:: https://raw.githubusercontent.com/earthobservations/wetterdienst/main/docs/img/hohenpeissenberg_warming_stripes.png\n        :alt: warming stripes of Hohenpeissenberg/Germany\n\n    *"We are the first generation to feel the effect of climate change and the last generation who can do something about it." - Barack Obama*\n\n.. overview_start_marker\n\nOverview\n########\n\n.. image:: https://github.com/earthobservations/wetterdienst/workflows/Tests/badge.svg\n   :target: https://github.com/earthobservations/wetterdienst/actions?workflow=Tests\n.. image:: https://codecov.io/gh/earthobservations/wetterdienst/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/earthobservations/wetterdienst\n.. image:: https://readthedocs.org/projects/wetterdienst/badge/?version=latest\n   :target: https://wetterdienst.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n\n.. image:: https://img.shields.io/pypi/pyversions/wetterdienst.svg\n   :target: https://pypi.python.org/pypi/wetterdienst/\n.. image:: https://img.shields.io/pypi/v/wetterdienst.svg\n   :target: https://pypi.org/project/wetterdienst/\n.. image:: https://img.shields.io/pypi/status/wetterdienst.svg\n   :target: https://pypi.python.org/pypi/wetterdienst/\n.. image:: https://pepy.tech/badge/wetterdienst/month\n   :target: https://pepy.tech/project/wetterdienst\n.. image:: https://img.shields.io/github/license/earthobservations/wetterdienst\n   :target: https://github.com/earthobservations/wetterdienst/blob/main/LICENSE\n.. image:: https://zenodo.org/badge/160953150.svg\n   :target: https://zenodo.org/badge/latestdoi/160953150\n\nIntroduction\n************\n\nWelcome to Wetterdienst, your friendly weather service library for Python.\n\nWe are a group of like-minded people trying to make access to weather data in\nPython feel like a warm summer breeze, similar to other projects like\nrdwd_ for the R language, which originally drew our interest in this project.\nOur long-term goal is to provide access to multiple weather services as well as other\nrelated agencies such as river measurements. With ``wetterdienst`` we try to use modern\nPython technologies all over the place. The library is based on pandas_ across the board,\nuses Poetry_ for package administration and GitHub Actions for all things CI.\nOur users are an important part of the development as we are not currently using the\ndata we are providing and only implement what we think would be the best. Therefore\ncontributions and feedback whether it be data related or library related are very\nwelcome! Just hand in a PR or Issue if you think we should include a new feature or data\nsource.\n\n.. _rdwd: https://github.com/brry/rdwd\n.. _pandas: https://pandas.pydata.org/\n.. _Poetry: https://python-poetry.org/\n\nAcknowledgements\n****************\n\nWe want to acknowledge all environmental agencies which provide their data open and free\nof charge first and foremost for the sake of endless research possibilities.\n\nWe want to acknowledge Jetbrains_ and their `open source team`_ for providing us with\nlicenses for Pycharm Pro, which we are using for the development.\n\nWe want to acknowledge all contributors for being part of the improvements to this\nlibrary that make it better and better every day.\n\n.. _Jetbrains: https://www.jetbrains.com/\n.. _open source team: https://github.com/JetBrains\n\nCoverage\n********\n\nDWD (Deutscher Wetterdienst / German Weather Service / Germany)\n    - Historical Weather Observations\n        - Historical (last ~300 years), recent (500 days to yesterday), now (yesterday up to last hour)\n        - Every minute to yearly resolution\n        - Time series of stations in Germany\n    - Mosmix - statistical optimized scalar forecasts extracted from weather models\n        - Point forecast\n        - 5400 stations worldwide\n        - Both MOSMIX-L and MOSMIX-S is supported\n        - Up to 115 parameters\n    - Radar\n        - 16 locations in Germany\n        - All of Composite, Radolan, Radvor, Sites and Radolan_CDC\n        - Radolan: calibrated radar precipitation\n        - Radvor: radar precipitation forecast\n\nECCC (Environnement et Changement Climatique Canada / Environment and Climate Change Canada / Canada)\n    - Historical Weather Observations\n        - Historical (last ~180 years)\n        - Hourly, daily, monthly, (annual) resolution\n        - Time series of stations in Canada\n\nNOAA (National Oceanic And Atmospheric Administration / National Oceanic And Atmospheric Administration / United States Of America)\n    - Global Historical Climatology Network\n        - Historical, daily weather observations from around the globe\n        - more then 100k stations\n        - data for weather services which don\'t publish data themselves\n\nTo get better insight on which data we have currently made available and under which\nlicense those are published take a look at the data_ section.\n\n.. _data: https://wetterdienst.readthedocs.io/en/latest/data/index.html\n\nFeatures\n********\n\n- API(s) for stations (metadata) and values\n- Get station(s) nearby a selected location\n- Define your request by arguments such as `parameter`, `period`, `resolution`,\n  `start date`, `end date`\n- Command line interface\n- Web-API via FastAPI\n- Run SQL queries on the results\n- Export results to databases and other data sinks\n- Public Docker image\n\nSetup\n*****\n\n``wetterdienst`` can be used by either installing it on your workstation or within a Docker\ncontainer.\n\nNative\n======\n\nVia PyPi (standard):\n\n.. code-block:: bash\n\n    pip install wetterdienst\n\nVia Github (most recent):\n\n.. code-block:: bash\n\n    pip install git+https://github.com/earthobservations/wetterdienst\n\nThere are some extras available for ``wetterdienst``. Use them like:\n\n.. code-block:: bash\n\n    pip install wetterdienst[http,sql]\n\n- docs: Install the Sphinx documentation generator.\n- ipython: Install iPython stack.\n- export: Install openpyxl for Excel export and pyarrow for writing files in Feather- and Parquet-format.\n- http: Install HTTP API prerequisites.\n- sql: Install DuckDB for querying data using SQL.\n- duckdb: Install support for DuckDB.\n- influxdb: Install support for InfluxDB.\n- cratedb: Install support for CrateDB.\n- mysql: Install support for MySQL.\n- postgresql: Install support for PostgreSQL.\n\nIn order to check the installation, invoke:\n\n.. code-block:: bash\n\n    wetterdienst --help\n\n.. _run-in-docker:\n\nDocker\n======\n\nDocker images for each stable release will get pushed to GitHub Container Registry.\n\nThere are images in two variants, ``wetterdienst-standard`` and ``wetterdienst-full``.\n\n``wetterdienst-standard`` will contain a minimum set of 3rd-party packages,\nwhile ``wetterdienst-full`` will try to serve a full environment by also\nincluding packages like GDAL and wradlib.\n\nPull the Docker image:\n\n.. code-block:: bash\n\n    docker pull ghcr.io/earthobservations/wetterdienst-standard\n\nLibrary\n-------\nUse the latest stable version of ``wetterdienst``:\n\n.. code-block:: bash\n\n    $ docker run -ti ghcr.io/earthobservations/wetterdienst-standard\n    Python 3.8.5 (default, Sep 10 2020, 16:58:22)\n    [GCC 8.3.0] on linux\n\n.. code-block:: python\n\n    import wetterdienst\n    wetterdienst.__version__\n\nCommand line script\n-------------------\nThe ``wetterdienst`` command is also available:\n\n.. code-block:: bash\n\n    # Make an alias to use it conveniently from your shell.\n    alias wetterdienst=\'docker run -ti ghcr.io/earthobservations/wetterdienst-standard wetterdienst\'\n\n    wetterdienst --help\n    wetterdienst version\n    wetterdienst info\n\nExample\n*******\n\nAcquisition of historical data for specific stations using ``wetterdienst`` as library:\n\nLoad required request class:\n\n.. code-block:: python\n\n    >>> import pandas as pd\n    >>> pd.set_option(\'max_columns\', 8)\n    >>> from wetterdienst.provider.dwd.observation import DwdObservationRequest\n\nAlternatively, though without argument/type hinting:\n\n.. code-block:: python\n\n    >>> from wetterdienst import Wetterdienst\n    >>> API = Wetterdienst("dwd", "observation")\n\nGet data:\n\n.. code-block:: python\n\n    >>> request = DwdObservationRequest(\n    ...    parameter=["climate_summary"],\n    ...    resolution="daily",\n    ...    start_date="1990-01-01",  # if not given timezone defaulted to UTC\n    ...    end_date="2020-01-01",  # if not given timezone defaulted to UTC\n    ...    tidy=True,  # default, tidy data\n    ...    humanize=True,  # default, humanized parameters\n    ...    si_units=True  # default, convert values to SI units\n    ... ).filter_by_station_id(station_id=(1048, 4411))\n    >>> request.df.head()  # station list\n         station_id                 from_date                   to_date  height  \\\n    209      01048 1934-01-01 00:00:00+00:00 ... 00:00:00+00:00   228.0\n    818      04411 1979-12-01 00:00:00+00:00 ... 00:00:00+00:00   155.0\n    <BLANKLINE>\n         latitude  longitude                    name    state\n    209   51.1278    13.7543       Dresden-Klotzsche  Sachsen\n    818   49.9195     8.9671  Schaafheim-Schlierbach   Hessen\n\n    >>> request.values.all().df.head()  # values\n      station_id          dataset      parameter                      date  value  \\\n    0      01048  climate_summary  wind_gust_max 1990-01-01 00:00:00+00:00    NaN\n    1      01048  climate_summary  wind_gust_max 1990-01-02 00:00:00+00:00    NaN\n    2      01048  climate_summary  wind_gust_max 1990-01-03 00:00:00+00:00    5.0\n    3      01048  climate_summary  wind_gust_max 1990-01-04 00:00:00+00:00    9.0\n    4      01048  climate_summary  wind_gust_max 1990-01-05 00:00:00+00:00    7.0\n    <BLANKLINE>\n       quality\n    0      NaN\n    1      NaN\n    2     10.0\n    3     10.0\n    4     10.0\n\n\nReceiving of stations for defined parameters using the ``wetterdienst`` client:\n\n.. code-block:: bash\n\n    # Get list of all stations for daily climate summary data in JSON format\n    wetterdienst dwd observations stations --parameter=kl --resolution=daily --period=recent\n\n    # Get daily climate summary data for specific stations\n    wetterdienst dwd observations values --station=1048,4411 --parameter=kl --resolution=daily --period=recent\n\nFurther examples (code samples) can be found in the `examples`_ folder.\n\n.. _examples: https://github.com/earthobservations/wetterdienst/tree/main/example\n\n.. overview_end_marker\n\nDocumentation\n*************\n\nWe strongly recommend reading the full documentation, which will be updated continuously\nas we make progress with this library:\n\nhttps://wetterdienst.readthedocs.io/\n\nFor the whole functionality, check out the `Usage documentation and examples`_ section of our\ndocumentation, which will be constantly updated. To stay up to date with the\ndevelopment, take a look at the changelog_. Also, don\'t miss out our examples_.\n\nData license\n************\n\nLicenses of the available data can be found in our documentation at the `data license`_\nsection. Licenses and usage requirements may differ so check this out before including\nthe data in your project to be sure to fulfill copyright issues beforehand.\n\n.. _data license: https://wetterdienst.readthedocs.io/en/latest/data/license.html\n\n.. contribution_development_marker\n\nContribution\n************\n\nThere are different ways in which you can contribute to this library:\n\n- by handing in a PR which describes the feature/issue that was solved including tests\n  for newly added features\n- by using our library and reporting bugs to us either by mail or by creating a new\n  Issue\n- by letting us know either via issue or discussion what function or data source we may\n  include into this library describing possible solutions or acquisition\n  methods/endpoints/APIs\n\nDevelopment\n***********\n\n1. Clone the library and install the environment.\n\n   This setup procedure will outline how to install the library and the minimum\n   dependencies required to run the whole test suite. If, for some reason, you\n   are not available to install all the packages, just leave out some of the\n   "extras" dependency tags.\n\n.. code-block:: bash\n\n    git clone https://github.com/earthobservations/wetterdienst\n    cd wetterdienst\n\n    # Prerequisites\n    brew install --cask firefox\n    brew install git python geckodriver\n\n    # Option 1: Basic\n    git clone https://github.com/earthobservations/wetterdienst\n    cd wetterdienst\n    python3 -m venv .venv\n    source .venv/bin/activate\n    pip install --requirement=requirements.txt\n    python setup.py develop\n\n    # (Option 2: Install package with extras)\n    pip install ".[sql,export,restapi,explorer]"\n\n    # Option 3: Install package with extras using poetry.\n    poetry install --extras=sql --extras=export --extras=restapi --extras=explorer\n    poetry shell\n\n2. For running the whole test suite, you will need to have Firefox and\n   geckodriver installed on your machine. Install them like::\n\n       # macOS\n       brew install --cask firefox\n       brew install geckodriver\n\n       # Other OS\n       # You can also get installers and/or release archives for Linux, macOS\n       # and Windows at\n       #\n       # - https://www.mozilla.org/en-US/firefox/new/\n       # - https://github.com/mozilla/geckodriver/releases\n\n   If this does not work for some reason and you would like to skip ui-related\n   tests on your machine, please invoke the test suite with::\n\n       poe test -m "not ui"\n\n3. Edit the source code, add corresponding tests and documentation for your\n   changes. While editing, you might want to continuously run the test suite\n   by invoking::\n\n       poe test\n\n   In order to run only specific tests, invoke::\n\n       # Run tests by module name or function name.\n       poe test -k test_cli\n\n       # Run tests by tags.\n       poe test -m "not (remote or slow)"\n\n4. Before committing your changes, please als run those steps in order to make\n   the patch adhere to the coding standards used here.\n\n.. code-block:: bash\n\n    poe format  # black code formatting\n    poe lint    # lint checking\n    poe export  # export of requirements (for Github Dependency Graph)\n\n5. Push your changes and submit them as pull request\n\n   Thank you in advance!\n\n\n.. note::\n\n    If you need to extend the list of package dependencies, invoke:\n\n    .. code-block:: bash\n\n        # Add package to runtime dependencies.\n        poetry add new-package\n\n        # Add package to development dependencies.\n        poetry add --dev new-package\n\n\n\nKnown Issues\n************\n\nMAC ARM64 (M1)\n==============\n\nYou need to install **pandas, numpy and scipy** as follows before continuing with the regular setup:\n\n.. code-block:: bash\n\n    pip install pandas --no-use-pep517\n    pip install numpy --no-use-pep517\n    pip install --no-binary :all: --no-use-pep517 scipy\n\nFurther additional libraries are affected and have to be installed in a similar manner:\n\n.. code-block:: bash\n\n    # SQL related\n    brew install postgresql\n    brew link openssl (and export ENVS as given)\n    pip install psycopg2-binary --no-use-pep517\n\nFurthermore as h5py is currently bound to versions of numpy that conflict with the ARM64 ready libraries, h5py itself as\nwell as wradlib are not available for users with that architecture!\n\nLINUX ARM (Raspberry Pi)\n========================\n\nRunning wetterdienst on Raspberry Pi, you need to install **numpy**\nand **lxml** prior to installing wetterdienst running the following\nlines:\n\n.. code-block:: bash\n\n    sudo apt-get install libatlas-base-dev\n    sudo apt-get install python3-lxml\n\nImportant Links\n***************\n\n- `Usage documentation and examples`_\n- `Changelog`_\n\n.. _Usage documentation and examples: https://wetterdienst.readthedocs.io/en/latest/usage/\n.. _Changelog: https://wetterdienst.readthedocs.io/en/latest/changelog.html\n',
    'author': 'Benjamin Gutzmann',
    'author_email': 'gutzemann@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://wetterdienst.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
