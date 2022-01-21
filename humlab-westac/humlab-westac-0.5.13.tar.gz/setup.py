# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notebooks',
 'notebooks.co_occurrence',
 'notebooks.legacy',
 'notebooks.legacy.scrachpads',
 'notebooks.legacy.tfidf_word_siginificance',
 'notebooks.most_discriminating_words',
 'notebooks.named_entity_recognition',
 'notebooks.political_in_newspapers',
 'notebooks.political_in_newspapers.notebook_gui',
 'notebooks.political_in_newspapers.scripts',
 'notebooks.pos_statistics',
 'notebooks.riksdagens_protokoll',
 'notebooks.riksdagens_protokoll.statistics',
 'notebooks.riksdagens_protokoll.token_counts',
 'notebooks.riksdagens_protokoll.topic_modeling',
 'notebooks.riksdagens_protokoll.topic_modeling.topic_trends',
 'notebooks.riksdagens_protokoll.word_trends',
 'notebooks.statens_offentliga_utredningar',
 'notebooks.textblock_politiskt',
 'notebooks.word_distribution_trends',
 'notebooks.word_trends']

package_data = \
{'': ['*']}

install_requires = \
['bokeh',
 'click',
 'humlab-penelope>=0.6.1,<0.7.0',
 'ipydatagrid>=1.1.8,<2.0.0',
 'ipywidgets==7.6.3',
 'jupyterlab==3.0.16',
 'loguru>=0.5.3,<0.6.0',
 'matplotlib',
 'msgpack>=1.0.2,<2.0.0',
 'nltk',
 'pandas',
 'pandas-bokeh',
 'scikit-learn',
 'scipy',
 'sklearn',
 'tqdm']

entry_points = \
{'console_scripts': ['parlaclarin-vectorize = '
                     'scripts.riksdagens_protokoll.parlaclarin.vectorize.py:process']}

setup_kwargs = {
    'name': 'humlab-westac',
    'version': '0.5.13',
    'description': 'Welfare State Analytics',
    'long_description': '# The Welfare State Analytics Text Analysis Repository\n\n## About the Project\n\nWelfare State Analytics. Text Mining and Modeling Swedish Politics, Media & Culture, 1945-1989 (WeStAc) is a digital humanities research project with five co-operatings partners: Umeå University, Uppsala University, Aalto University (Finland) and the National Library of Sweden.\n\nThe project will digitise literature, curate already digitised collections, and perform research via probabilistic methods and text mining models. WeStAc will both digitise and curate three massive textual datasets—in all, Big Data of almost four billion tokens—from the domains of Swedish politics, news media and literary culture during the second half of the 20th century.\n\n## Installation\n\n### Local install using pipenv\n\nSee [this page](https://github.com/humlab/welfare_state_analytics/wiki/How-to:-Install-notebooks-on-local-machine).\n\n### JupyterHub installation\n\nThe `westac_hub` repository contains a ready-to-use Docker setup (`Dockerfile` and `docker-compose.yml`) for a Jupyter Hub using `nginx` as reverse-proxy. The default setup uses `DockerSpawner` that spawns containers as specified in `westac_lab`, and Github for autorization (OAuth2). See the Makefile on how to build the project.\n\n### Single Docker container\n\nYou can also run the `westac_lab` container as a single Docker container if you have Docker installed on your computer.\n',
    'author': 'Roger Mähler',
    'author_email': 'roger.mahler@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://westac.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<3.9.0',
}


setup(**setup_kwargs)
