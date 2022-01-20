# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['c4v',
 'c4v.classifier',
 'c4v.classifier.data_gathering',
 'c4v.classifier.language_model',
 'c4v.cloud',
 'c4v.dashboard',
 'c4v.data',
 'c4v.microscope',
 'c4v.scraper',
 'c4v.scraper.crawler',
 'c4v.scraper.crawler.crawlers',
 'c4v.scraper.persistency_manager',
 'c4v.scraper.scraped_data_classes',
 'c4v.scraper.scrapers',
 'c4v.scraper.spiders']

package_data = \
{'': ['*']}

install_requires = \
['Scrapy>=2.5.0,<3.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'click==7.1.2',
 'dynaconf>=3.1.4,<4.0.0',
 'importlib-metadata>=4.6.1,<5.0.0',
 'importlib-resources>=5.2.2,<6.0.0',
 'nbconvert==5.6.1',
 'nltk>=3.5,<4.0',
 'pip>=21.0.0,<22.0.0',
 'pytz>=2021.3,<2022.0',
 'scrapydo>=0.2.2,<0.3.0',
 'tabulate>=0.8.9,<0.9.0',
 'traitlets==4.3.3',
 'zipp>=3.5.0,<4.0.0']

extras_require = \
{':extra == "classification" or extra == "all"': ['datasets>=1.10.2,<2.0.0'],
 ':python_version >= "3.6.1" and python_version < "3.7"': ['dataclasses>=0.8.0,<0.9.0'],
 'all': ['tensorflow>=2.5.2,<3.0.0',
         'tensorflow_hub[make_image_classifier]==0.8.0',
         'tensorflow-probability==0.10.0',
         'scikit-learn==0.23.1',
         'scikit-multilearn==0.2.0',
         'pandas==1.1.1',
         'google-cloud-bigquery==1.26.1',
         'google-cloud-logging>=2.7.0,<3.0.0',
         'ipykernel==5.5.5',
         'ipython==7.16.1',
         'transformers>=4.9.0,<5.0.0',
         'torch>=1.9.0,<1.10.0',
         'transformers-interpret>=0.5.2,<0.6.0',
         'streamlit>=1.2.0,<2.0.0',
         'Flask>=2.0.2,<3.0.0',
         'google-cloud-storage>=1.43.0,<2.0.0',
         'google-cloud-functions>=1.4.0,<2.0.0',
         'firebase-admin>=5.2.0,<6.0.0'],
 'classification': ['scikit-learn==0.23.1',
                    'scikit-multilearn==0.2.0',
                    'pandas==1.1.1',
                    'transformers>=4.9.0,<5.0.0',
                    'torch>=1.9.0,<1.10.0',
                    'transformers-interpret>=0.5.2,<0.6.0'],
 'dashboard': ['streamlit>=1.2.0,<2.0.0'],
 'gcloud': ['google-cloud-bigquery==1.26.1',
            'google-cloud-logging>=2.7.0,<3.0.0',
            'Flask>=2.0.2,<3.0.0',
            'google-cloud-storage>=1.43.0,<2.0.0',
            'google-cloud-functions>=1.4.0,<2.0.0',
            'firebase-admin>=5.2.0,<6.0.0'],
 'jupyter': ['ipykernel==5.5.5', 'ipython==7.16.1'],
 'tensorflow': ['tensorflow>=2.5.2,<3.0.0',
                'tensorflow_hub[make_image_classifier]==0.8.0',
                'tensorflow-probability==0.10.0']}

entry_points = \
{'console_scripts': ['c4v = c4v.c4v_cli:c4v_cli']}

setup_kwargs = {
    'name': 'c4v-py',
    'version': '0.1.0.dev20221121',
    'description': 'Code for Venezuela python library.',
    'long_description': '# c4v-py\n\n<p align="center">\n  <img width="125" src="assets/logo.png">\n</p>\n\n> Solving Venezuela pressing matters one commmit at a time\n\n`c4v-py` is a library used to address Venezuela\'s pressing issues\nusing computer and data science. Check the [online documentation](https://code-for-venezuela.github.io/c4v-py/)\n\n- [Installation](#installation)\n- [Development](#development)\n- [Pending](#pending)\n\n## Installation\n\nUse pip to install the package:\n\n```python3\npip install c4v-py\n```\n\n## Usage\n\n_TODO_\n\n[Can you help us? Open a new issue in\nminutes!](https://github.com/code-for-venezuela/c4v-py/issues/new/choose)\n\n## Contributing\n\nThe following tools are used in this project:\n\n- [Poetry](https://python-poetry.org/) is used as package manager.\n- [Nox](https://nox.thea.codes/) is used as automation tool, mainly for testing.\n- [Black](https://black.readthedocs.io/) is the mandatory formatter tool.\n- [PyEnv](https://github.com/pyenv/pyenv/wiki) is recommended as a tool to handle multiple python versions in your machine.\n\nThe library is intended to be compatible with python ~3.6.9, ~3.7.4 and ~3.8.2. But the primary version to support is ~3.8.2.\n\nThe general structure of the project is trying to follow the recommendations\nin [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/).\nThe main difference lies in the source code itself which is not constraint to data science code.\n\n### Setup\n\n1. Install pyenv and select a version, ie: 3.8.2. Once installed run `pyenv install 3.8.2`\n2. Install poetry in your system\n3. Clone this repo in a desired location `git clone https://github.com/code-for-venezuela/c4v-py.git`\n4. Navigate to the folder `cd c4v-py`\n5. Make sure your poetry picks up the right version of python by running `pyenv local 3.8.2`, if 3.8.2 is your right version.\n6. Since our toml file is already created, we need to get all dependencies by running `poetry install`. This step might take a few minutes to complete.\n7. Install nox\n8. From `c4v-py` directory, on your terminal, run the command `nox -s tests` to make sure all the tests run.\n\nIf you were able to follow every step with no error, you are ready to start contributing. Otherwise, [open a new issue](https://github.com/code-for-venezuela/c4v-py/issues/new/choose)!\n\n## Roadmap\n\n- [ ] Add CONTRIBUTING guidelines\n- [ ] Add issue templates\n- [ ] Document where to find things (datasets, more info, etc.)\n  - This might be done (in conjunction) with Github Projects. Managing tasks there might be a good idea.\n- [ ] Add LICENSE\n- [ ] Change the authors field in pyproject.toml\n- [ ] Change the repository field in pyproject.toml\n- [ ] Move the content below to a place near to the data in the data folder or use the reference folder.\n      Check [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/) for details.\n- [ ] Understand what is in the following folders and decide what to do with them.\n  - [ ] brat-v1.3_Crunchy_Frog\n  - [ ] creating_models\n  - [x] data/data_to_annotate\n  - [ ] data_analysis\n- [ ] Set symbolic links between `brat-v1.3_Crunchy_Frog/data` and `data/data_to_annotate`. `data_sampler` extracts to `data/data_to_annotate`. Files placed here are read by Brat.\n  - [ ] Download Brat - `wget https://brat.nlplab.org/index.html`\n  - [ ] untar brat - `tar -xzvf brat-v1.3_Crunchy_Frog.tar.gz`\n  - [ ] install brat - `cd brat-v1.3_Crunchy_Frog && ./install.sh`\n  - [ ] replace default annotation conf for current configuration - `wget https://raw.githubusercontent.com/dieko95/c4v-py/master/brat-v1.3_Crunchy_Frog/annotation.conf -O annotation.conf`\n  - [ ] replace default config.py for current configuration - `wget https://raw.githubusercontent.com/dieko95/c4v-py/master/brat-v1.3_Crunchy_Frog/config.py -O config.py`\n',
    'author': 'Edilmo Palencia',
    'author_email': 'edilmo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.codeforvenezuela.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
