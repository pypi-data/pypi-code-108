# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['digital_twin_distiller',
 'digital_twin_distiller.data_store',
 'digital_twin_distiller.platforms',
 'digital_twin_distiller.resources.model_template']

package_data = \
{'': ['*'],
 'digital_twin_distiller': ['resources/doc_template/*',
                            'resources/doc_template/docs/*',
                            'resources/doc_template/docs/images/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'Shapely>=1.8.0,<2.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'ezdxf>=0.16.5,<0.17.0',
 'fastapi>=0.70,<0.71',
 'fasttext>=0.9.2,<0.10.0',
 'gensim>=4.1.2,<5.0.0',
 'gmsh>=4.8.4,<5.0.0',
 'importlib-resources>=5.4.0,<6.0.0',
 'mkdocs-git-revision-date-plugin>=0.3.1,<0.4.0',
 'mkdocs-material>=7.3.6,<8.0.0',
 'mkdocs>=1.2.3,<2.0.0',
 'mkdocstrings>=0.16.2,<0.17.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pygmsh>=7.1.13,<8.0.0',
 'python-markdown-math>=0.8,<0.9',
 'pyvista>=0.32.1,<0.33.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'sklearn>=0.0,<0.1',
 'svgpathtools>=1.4.2,<2.0.0',
 'tika>=1.24,<2.0',
 'tqdm>=4.62.3,<5.0.0',
 'uvicorn>=0.15.0,<0.16.0',
 'vedo>=2021,<2022']

entry_points = \
{'console_scripts': ['digital-twin-distiller = '
                     'digital_twin_distiller.cli:optimize_cli']}

setup_kwargs = {
    'name': 'digital-twin-distiller',
    'version': '2022.1',
    'description': 'Python project for creating a long-lasting, encapsulated version of your numerical simulation or your machine-learning-based project.',
    'long_description': None,
    'author': 'MONTANA Knowledge Management ltd.',
    'author_email': 'info@distiller.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
