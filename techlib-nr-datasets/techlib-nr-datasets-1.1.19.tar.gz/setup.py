# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nr_datasets',
 'nr_datasets.datamodels',
 'nr_datasets.jsonschemas',
 'nr_datasets.jsonschemas.nr_datasets',
 'nr_datasets.mapping_includes',
 'nr_datasets.mapping_includes.v7',
 'nr_datasets.mappings',
 'nr_datasets.mappings.v7',
 'nr_datasets.mappings.v7.nr_datasets',
 'nr_datasets.marshmallow']

package_data = \
{'': ['*']}

install_requires = \
['oarepo-doi-generator>=1.0.6,<2.0.0',
 'oarepo-tokens>=0.1.9,<0.2.0',
 'oarepo>=3.3.59,<4.0.0',
 'techlib-nr-datasets-metadata>=3.0,<4.0']

entry_points = \
{'invenio_base.api_apps': ['nr_datasets = nr_datasets:NRDatasets'],
 'invenio_base.apps': ['nr_datasets = nr_datasets:NRDatasets'],
 'invenio_jsonschemas.schemas': ['nr_datasets = nr_datasets.jsonschemas'],
 'invenio_pidstore.fetchers': ['nr_datasets = '
                               'nr_datasets.fetchers:nr_datasets_id_fetcher'],
 'invenio_pidstore.minters': ['nr_datasets = '
                              'nr_datasets.minters:nr_datasets_id_minter'],
 'invenio_search.mappings': ['nr_datasets = nr_datasets.mappings'],
 'oarepo_mapping_includes': ['nr_datasets = nr_datasets.mapping_includes'],
 'oarepo_model_builder.datamodels': ['nr_datasets = nr_datasets.datamodels']}

setup_kwargs = {
    'name': 'techlib-nr-datasets',
    'version': '1.1.19',
    'description': 'Czech National Repository datasets data model.',
    'long_description': '# NR-Datasets\n\n[![Build Status](https://travis-ci.org/Narodni-repozitar/nr-datasets.svg?branch=master)](https://travis-ci.org/Narodni-repozitar/nr-datasets)\n[![Coverage Status](https://coveralls.io/repos/github/Narodni-repozitar/nr-datasets/badge.svg?branch=master)](https://coveralls.io/github/Narodni-repozitar/nr-datasets?branch=master)\n\n\nDisclaimer: The library is part of the Czech National Repository, and therefore the README is written in Czech.\nGeneral libraries extending [Invenio](https://github.com/inveniosoftware) are concentrated under the [Oarepo\n namespace](https://github.com/oarepo).\n\n  ## Instalace\n\n Nejedná se o samostatně funkční knihovnu, proto potřebuje běžící Invenio a závislosti Oarepo.\n Knihovna se instaluje ze zdroje.\n\n ```bash\ngit clone git@github.com:Narodni-repozitar/nr-datasets.git\ncd nr-datasets\npip install poetry\npoetry install\n```\n\nPro testování a/nebo samostané fungování knihovny je nutné instalovat tests z extras.\n\n```bash\npoetry install --extras tests\n```\n\n:warning: Pro instalaci se používá Manažer závilostí **Poetry** více infromací lze naleznout v\n[dokumentaci](https://python-poetry.org/docs/)\n',
    'author': 'Miroslav Bauer',
    'author_email': 'Miroslav.Bauer@cesnet.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
