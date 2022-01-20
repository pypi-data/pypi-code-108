# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ou_sphinx_theme', 'ou_sphinx_theme.ext']

package_data = \
{'': ['*'],
 'ou_sphinx_theme': ['static/*',
                     'static/icons/*',
                     'static/mathjax/*',
                     'static/mathjax/a11y/*',
                     'static/mathjax/adaptors/*',
                     'static/mathjax/input/*',
                     'static/mathjax/input/mml/*',
                     'static/mathjax/input/mml/extensions/*',
                     'static/mathjax/input/tex/extensions/*',
                     'static/mathjax/output/*',
                     'static/mathjax/output/chtml/fonts/*',
                     'static/mathjax/output/chtml/fonts/woff-v2/*',
                     'static/mathjax/output/svg/fonts/*',
                     'static/mathjax/sre/*',
                     'static/mathjax/sre/mathmaps/*',
                     'static/mathjax/ui/*']}

entry_points = \
{'sphinx.html_themes': ['openuniversity = ou_sphinx_theme']}

setup_kwargs = {
    'name': 'ou-sphinx-theme',
    'version': '1.2.0',
    'description': '',
    'long_description': None,
    'author': 'Mark Hall',
    'author_email': 'mark.hall@open.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
