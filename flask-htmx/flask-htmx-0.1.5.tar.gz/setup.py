# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_htmx']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0']

setup_kwargs = {
    'name': 'flask-htmx',
    'version': '0.1.5',
    'description': 'A Flask extension to work with HTMX.',
    'long_description': '##########\nFlask-HTMX\n##########\n\n.. image:: https://badge.fury.io/py/flask-htmx.svg\n    :target: https://badge.fury.io/py/flask-htmx\n\n.. image:: https://readthedocs.org/projects/flask-htmx/badge/?version=latest\n    :target: https://flask-htmx.readthedocs.io/en/latest/?badge=latest\n    :alt: Documentation Status\n\n\n.. image:: https://codecov.io/gh/edmondchuc/flask-htmx/branch/main/graph/badge.svg?token=K6YB3PB33T\n    :target: https://codecov.io/gh/edmondchuc/flask-htmx\n\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\n.. image:: https://img.shields.io/badge/License-MIT-red.svg\n    :target: https://github.com/edmondchuc/flask-htmx/blob/main/LICENSE\n\n.. image:: https://static.pepy.tech/personalized-badge/flask-htmx?period=month&units=international_system&left_color=grey&right_color=blue&left_text=downloads/week\n    :target: https://pepy.tech/project/flask-htmx\n\n.. image:: https://static.pepy.tech/personalized-badge/flask-htmx?period=month&units=international_system&left_color=grey&right_color=blue&left_text=downloads/month\n    :target: https://pepy.tech/project/flask-htmx\n\n.. image:: https://static.pepy.tech/personalized-badge/flask-htmx?period=total&units=international_system&left_color=grey&right_color=blue&left_text=downloads\n    :target: https://pepy.tech/project/flask-htmx\n\nA Flask extension to work with HTMX.\n\nDocumentation: https://flask-htmx.readthedocs.io\n\n.. quickstart-startblock\n\nQuickstart\n==========\n\nInstall the extension with pip.\n\n.. code-block:: bash\n\n    pip install flask-htmx\n\nOr perhaps you use Poetry.\n\n.. code-block:: bash\n\n    poetry add flask-htmx\n\nYou can register the HTMX object by passing the Flask\n:code:`app` object via the constructor.\n\n.. code-block:: python\n\n    htmx = HTMX(app)\n\nOr you can register the HTMX object using\n`HTMX.init_app() <https://flask-htmx.readthedocs.io/en/latest/flask_htmx.htmx.html#flask_htmx.htmx.HTMX.init_app>`_.\n\n.. code-block:: python\n\n    htmx = HTMX()\n    htmx.init_app(app)\n\nA minimal working example.\n\n.. code-block:: python\n\n    from flask import Flask\n    from flask_htmx import HTMX\n\n    app = Flask(__name__)\n    htmx = HTMX(app)\n\n    @app.route("/")\n    def home():\n        if htmx:\n            return render_template("partials/thing.html")\n        return render_template("index.html")\n\nThe above example checks whether the request came\nfrom HTMX or not. If :code:`htmx` evaluates to\n`True <https://docs.python.org/3/library/constants.html#True>`_, then it was a HTMX request, else\n`False <https://docs.python.org/3/library/constants.html#False>`_.\n\nThis allows you to return a partial\nHTML when it\'s a HTMX request or the full page HTML\nwhen it is a normal browser request.\n\nFlask-HTMX also supports checking for HTMX headers\nduring a request in the view. For example, check\nthe current URL of the browser of a HTMX request.\n\n.. code-block:: python\n\n    @app.route("/")\n    def home():\n        current_url = htmx.current_url\n        return render_template("index.html", current_url=current_url)\n\nOther HTMX request headers are also available.\nSee https://htmx.org/reference/#request_headers.\n\nContinue to the next section of the docs,\n`The HTMX Class <https://flask-htmx.readthedocs.io/en/latest/flask_htmx.htmx.html>`_.\n\n.. quickstart-endblock\n\nDevelopment\n===========\n\nInstallation\n------------\n\n.. code-block:: bash\n\n    poetry install\n\nRunning tests\n-------------\n\n.. code-block:: bash\n\n    poetry run pytest\n\nCoverage\n--------\n\n.. code-block:: bash\n\n    poetry run pytest --cov=flask_htmx tests/\n\nDocs\n----\n\n.. code-block:: bash\n\n    sphinx-autobuild docs docs/_build/html\n',
    'author': 'Edmond Chuc',
    'author_email': 'edmond.chuc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/edmondchuc/flask-htmx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
