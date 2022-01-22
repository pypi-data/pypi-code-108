# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['olapy',
 'olapy.core',
 'olapy.core.mdx',
 'olapy.core.mdx.executor',
 'olapy.core.mdx.executor.spark',
 'olapy.core.mdx.parser',
 'olapy.core.mdx.tools',
 'olapy.core.services',
 'olapy.core.services.spark',
 'olapy.etl']

package_data = \
{'': ['*'], 'olapy.etl': ['input_dir/*']}

install_requires = \
['attrs',
 'click',
 'lxml',
 'pandas',
 'pyyaml>=4.2b1',
 'regex',
 'spyne>=2.13,<3.0',
 'sqlalchemy',
 'typing',
 'xmlwitch']

extras_require = \
{'etl': ['awesome-slugify',
         'bonobo',
         'bonobo-sqlalchemy<0.6.1',
         'python-dotenv',
         'whistle<1.0.1'],
 'spark': ['pyspark<3']}

entry_points = \
{'console_scripts': ['etl = olapy.etl.etl:run_etl',
                     'olapy = olapy.__main__:cli']}

setup_kwargs = {
    'name': 'olapy',
    'version': '0.8.2',
    'description': 'OlaPy, an experimental OLAP engine based on Pandas',
    'long_description': "OlaPy, an experimental OLAP engine based on Pandas\n==================================================\n\nAbout\n-----\n\n**OlaPy** is an OLAP_ engine based on Python, which gives you a set of tools for the development of reporting and analytical\napplications, multidimensional analysis, and browsing of aggregated data with MDX_ and XMLA_ support.\n\n\n.. _OLAP: https://en.wikipedia.org/wiki/Online_analytical_processing\n.. _MDX: https://en.wikipedia.org/wiki/MultiDimensional_eXpressions\n.. _XMLA: https://en.wikipedia.org/wiki/XML_for_Analysis\n\n`Documentation <https://olapy.readthedocs.io/en/latest/>`_\n\n.. image:: https://raw.githubusercontent.com/abilian/olapy/master/docs/pictures/olapy.gif\n\nStatus\n~~~~~~\n\nThis project is currently a research prototype, not suited for production use.\n\n\n.. image:: https://static.pepy.tech/badge/olapy\n   :target: https://pepy.tech/project/olapy\n\nLicence\n~~~~~~~\n\nThis project is currently licenced under the LGPL v3 licence.\n\nInstallation\n------------\n\nInstall from PyPI\n~~~~~~~~~~~~~~~~~\n\nYou can install it directly from the `Python Package Index <https://pypi.python.org/pypi/olapy>`_::\n\n    pip install olapy\n\n\nInstall from Github\n~~~~~~~~~~~~~~~~~~~\n\nThe project sources are stored in `Github repository <https://github.com/abilian/olapy>`_.\n\nDownload from Github::\n\n    git clone git://github.com/abilian/olapy.git\n\n\nTo set up the application, run, ideally in a virtualenv::\n\n    cd olapy\n    python setup.py install\n\nor just::\n\n    pip install -e .\n\n**[OPTIONAL]**\n\nyou can use `Spark <https://spark.apache.org/docs/0.9.0/python-programming-guide.html>`_  instead of `Pandas <https://pandas.pydata.org/>`_, to do so, you need just to install it::\n\n    pip install pyspark\n\nand if you want to go back to pandas just uninstall spark with::\n\n    pip uninstall pyspark\n\nUsage\n-----\n\nBefore running OlaPy, you need to initialize it with::\n\n    olapy init\n\nand then you can run the server with::\n\n    olapy runserver\n\n\nand then from excel, open new spreadsheet and go to : Data -> From Other Sources -> From Analysis Services and use http://127.0.0.1:8000/ as server name and click next, then you can chose one of default olapy demo cubes (sales, foodmart...) and finish.\n\nthat's it ! now you can play with data\n\n\nDeveloping\n----------\n\nThis project must adhere to the `Abilian Developer Guide <http://abilian-developer-guide.readthedocs.io/>`_.\n\nPull requests are welcome.\n\nTests\n~~~~~\n\nTo run tests, run::\n\n    pytest tests\n\nor simply (on Unix-like systems)::\n\n    make test\n\n\nCredits\n-------\n\nThis project is developed by `Abilian SAS <https://www.abilian.com>`_ and partially funded by the French Government through the `Wendelin <http://www.wendelin.io/>`_ project and the `Investissement d'avenir <http://www.gouvernement.fr/investissements-d-avenir-cgi>`_ programme.\n",
    'author': 'Abilian SAS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abilian/olapy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
