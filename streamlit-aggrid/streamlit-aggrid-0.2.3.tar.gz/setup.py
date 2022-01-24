# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['st_aggrid']

package_data = \
{'': ['*'],
 'st_aggrid': ['frontend/*',
               'frontend/build/*',
               'frontend/build/static/css/*',
               'frontend/build/static/js/*',
               'frontend/public/*']}

install_requires = \
['pandas>=1.2',
 'python-dotenv>=0.19.1,<0.20.0',
 'simplejson>=3.0',
 'streamlit>=0.87.0']

setup_kwargs = {
    'name': 'streamlit-aggrid',
    'version': '0.2.3',
    'description': 'Streamlit component implementation of ag-grid',
    'long_description': "# streamlit-aggrid\n\n[![Open in Streamlit][share_badge]][share_link] [![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link] \n\nAgGrid is an awsome grid for web frontend. More information in [https://www.ag-grid.com/](https://www.ag-grid.com/). Consider purchasing a license from Ag-Grid if you are going to use enterprise features!\n\nComment on [discuss.streamlit.io](https://discuss.streamlit.io/t/ag-grid-component-with-input-support/) If you like it or [Buy me a beer 🍺!](https://www.paypal.com/donate?hosted_button_id=8HGLA4JZBYFPQ)\n\n<br>\n\nSome basic documentation is available: https://streamlit-aggrid.readthedocs.io\n# Install\n```\npip install streamlit-aggrid\n\n```\n\n# Quick Use\nCreate an example.py file\n```python\nfrom st_aggrid import AgGrid\nimport pandas as pd\n\ndf = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv')\nAgGrid(df)\n```\nRun :\n```shell\nstreamlit run example.py\n```\n\n# Demo\nGrid data is sent back to streamlit and can be reused in other components. In the example below a chart is updated on grid edition.\n\n![example image](https://github.com/PablocFonseca/streamlit-aggrid/raw/main/group_selection_example.gif)\n\n# Development Notes\nVersion 0.2.3\n* small fixes\n* Merged PR #44 and #25 (thanks [msabramo](https://github.com/msabramo) and [ljnsn](https://github.com/ljnsn))\n\nVersion 0.2.2\n* Updated frontend dependencies to latest version\n* Corrected text color for better viz when using streamlit theme (thanks [jasonpmcculloch](https://github.com/jasonpmcculloch))\n* Switched default theme to Balham Light ('light'), if you want to use streamlit theme set `theme='streamlit'` on agGrid call \n\n\nVersion 0.2.0\n* Support Themes\n* Incorporated Pull Requests with fixes and pre-select rows (Thanks [randomseed42](https://github.com/randomseed42) and [msabramo](https://github.com/msabramo))\n* You can use strings instead of importing GridUpdateMode and DataReturnMode enumerators\n* it works fine with st.forms!\n* new theme example in example folder\n\nVersion 0.1.9\n* Small fixes \n* Organized examples folder\n\nVersion 0.1.8\n* Fixes a bug that breaks the grid when NaN or Inf values are present in the data\n\nVersion 0.1.7\n* Fixes a bug that happened when converting data back from the grid with only one row\n* Added license_key parameter on AgGrid call.\n\nVersion 0.1.6\n* Fixes issue [#3](https://github.com/PablocFonseca/streamlit-aggrid/issues/3)\n* Adds support for timedelta columns check [example][share_link]\n\nVersion 0.1.5\n* small bug fixes\n* there is an option to avoid grid re-initialization on app update (check fixed_key_example.py on examples folder or [here](https://share.streamlit.io/pablocfonseca/streamlit-aggrid/main/examples/fixed_key_example.py))\n\nVersion 0.1.3\n* Fixed bug where cell was blank after edition.\n* Added enable_enterprise_modules argument to AgGrid call for enabling/disabling [enterprise features](https://www.ag-grid.com/documentation/javascript/licensing/)\n* It is now possible to inject js functions on gridOptions. Enabling advanced customizations such as conditional formating (check 4<sup>th</sup> column on the [example](share_link))\n\nVersion 0.1.2\n* added customCurrencyFormat as column type\n\n Version 0.1.0:\n* I worked a little bit more on making the example app functional.\n* Couple configuration options for update mode (How frontend updates streamlit) and for data returns (grid should return data filtered? Sorted?)\n* Some basic level of row selection\n* Added some docstrings specially on gridOptionsBuilder methods\n* Lacks performance for production. JS Client code is slow...\n\n\n[share_badge]: https://static.streamlit.io/badges/streamlit_badge_black_white.svg\n[share_link]: https://share.streamlit.io/pablocfonseca/streamlit-aggrid/main/examples/example.py\n\n[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label\n[github_link]: https://github.com/PablocFonseca/streamlit-aggrid\n\n[pypi_badge]: https://badgen.net/pypi/v/streamlit-aggrid?icon=pypi&color=black&label?\n[pypi_link]: https://www.pypi.org/project/streamlit-aggrid/\n",
    'author': 'Pablo Fonseca',
    'author_email': 'pablo.fonseca+pip@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PablocFonseca/streamlit-aggrid',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
