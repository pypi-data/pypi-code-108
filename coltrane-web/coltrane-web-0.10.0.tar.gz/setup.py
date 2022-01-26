# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coltrane',
 'coltrane.config',
 'coltrane.management',
 'coltrane.management.commands']

package_data = \
{'': ['*'], 'coltrane': ['templates/coltrane/*']}

install_requires = \
['Django>3.0',
 'click>=8.0.0,<9.0.0',
 'markdown-it-py>=2.0.1,<3.0.0',
 'markdown2>=2.4.2,<3.0.0',
 'mdit-py-plugins>=0.3.0,<0.4.0',
 'python-dotenv>0.17']

extras_require = \
{'deploy': ['gunicorn>=20.1.0,<21.0.0', 'whitenoise>=5.3.0,<6.0.0'],
 'docs': ['Sphinx>=4.3.2,<5.0.0',
          'linkify-it-py>=1.0.3,<2.0.0',
          'myst-parser>=0.16.1,<0.17.0',
          'furo>=2021.11.23,<2022.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0']}

entry_points = \
{'console_scripts': ['coltrane = coltrane.console:cli']}

setup_kwargs = {
    'name': 'coltrane-web',
    'version': '0.10.0',
    'description': 'A simple content site framework that harnesses the power of Django without the hassle.',
    'long_description': '<p align="center">\n  <a href="https://coltrane.readthedocs.io"><h1 align="center">coltrane</h1></a>\n</p>\n<p align="center">A simple content site framework that harnesses the power of Django without the hassle 🎵</p>\n\n![PyPI](https://img.shields.io/pypi/v/coltrane-web?color=blue&style=flat-square)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/coltrane-web?color=blue&style=flat-square)\n![GitHub Sponsors](https://img.shields.io/github/sponsors/adamghill?color=blue&style=flat-square)\n\n📖 Complete documentation: https://coltrane.readthedocs.io\n\n📦 Package located at https://pypi.org/project/coltrane-web/\n\n## ⭐ Features\n\n- Can either generate a static HTML, be used as a standalone Django site, or integrated into an existing Django site\n- Write content in markdown and render it in HTML\n- Use data from JSON files in templates and content\n- All the power of Django templates, template tags, and filters\n- Can include other Django apps for additional functionality\n- Opinionated Django project setup where everything works "out of the box"\n\n## ⚡ Quick start for a new static site\n\n1. `mkdir new-site && cd new-site` to create a new folder\n1. `poetry init --no-interaction --dependency coltrane-web:latest && poetry install` to create a new virtual environment and install `coltrane`\n1. `poetry run coltrane create` to create the folder structure for a new site\n1. Update `content/index.md`\n1. `poetry run coltrane play` for a local development server\n1. Go to http://localhost:8000 to see the updated markdown rendered into HTML\n1. `poetry run coltrane record` to output the rendered HTML files\n\n## Optional\n\n- Enable `watchman` for less resource-intensive autoreload on Mac: `brew install watchman`\n\n## How to add new content\n\nAdd markdown files or sub-directories with msrkdown files to the `content` directory and they will automatically have routes created that can be requested.\n\nWith this folder structure:\n\n```\n/content/index.md\n/content/about.md\n/content/articles/this-is-the-first-article.md\n```\n\nThere will be these URLs available:\n\n- `http://localhost:8000/` which serves HTML generated from the `/content/index.md` file\n- `http://localhost:8000/about` which serves HTML generated from the `/content/about.md` file\n- `http://localhost:8000/articles/this-is-the-first-article` which serves HTML generated from the `/content/articles/this-is-the-first-article.md` file\n\nRead all of the documentation at https://coltrane.readthedocs.io.\n',
    'author': 'adamghill',
    'author_email': 'adam@adamghill.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adamghill/coltrane/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>3.6.2,<4.0',
}


setup(**setup_kwargs)
