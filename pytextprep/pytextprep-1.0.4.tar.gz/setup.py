# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pytextprep']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'nltk>=3.6.7,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'wordcloud>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'pytextprep',
    'version': '1.0.4',
    'description': 'Performs pre-processing of tweets',
    'long_description': '[![ci-cd](https://github.com/UBC-MDS/pytextprep/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/pytextprep/actions/workflows/ci-cd.yml)\n# pytextprep\n\nThis is a Python package that offers additional text preprocessing functionality specifically designed for tweets. The package bundles functions to help with cleaning and gaining insight into tweet data, providing additional resources for EDA or enabling feature engineering.\n\n\nThe main functions of this package are:\n\n- `remove_punct` : Removes punctuation from a list of tweets\n    \n- `extract_ngram`: Extracts n-grams from a list of tweets\n    \n- `extract_hashtags`: Creates a list of hashtags from a list of tweets\n    \n- `generate_cloud`: Creates a word cloud of the most frequent words from a list of tweets\n\n\nIn the Python ecosystem the only popular package focused on tweet data is [tweet-preprocessor](https://pypi.org/project/tweet-preprocessor/). Even though this package is also customized specifically for dealing with Tweeter data its scope is solely oriented to tokenizing and cleaning the tweets. In contrast, our package can be leveraged to extract new features out of tweets.\n\n## Installation\n\nInstall from source:\n\n```bash\npip install git+https://github.com/UBC-MDS/pytextprep\n```\n\n## Usage\n\n```python\nfrom pytextprep.extract_ngram import extract_ngram\nfrom pytextprep.extract_hashtags import extract_hashtags\nfrom pytextprep.remove_punct import remove_punct\nfrom pytextprep.generate_cloud import generate_cloud\nimport matplotlib.pyplot as plt\n\ntweets_list = ["Make America Great Again! @DonalTrump", "It\'s a new day in #America"]\nextract_ngram(tweets_list, n=3)\n```\n\n```\n[\'Make America Great\', \'America Great Again!\', \'Great Again! @DonalTrump\', "Again! @DonalTrump It\'s", "@DonalTrump It\'s a", "It\'s a new", \'a new day\', \'new day in\', \'day in #America\']\n```\n\n```python\nextract_hashtags(tweets_list)\n```\n\n```\n[\'America\']\n```\n\n```python\nremove_punct(tweets_list, skip=["\'", "@", "#", \'-\'])\n```\n\n```\n[\'Make America Great Again @DonalTrump\', "It\'s a new day in #America"]\n```\n\n```python\nfig, wc = generate_cloud(tweets_list)\nplt.show()\n```\n\n![word_cloud](https://github.com/UBC-MDS/pytextprep/blob/main/docs/word_cloud.png)\n\n## Contributing\n\nContributors: Arijeet Chatterjee, Joshua Sia, Melisa Maidana, Philson Chan (DSCI_524_GROUP21).\n\nInterested in contributing? Check out the [contributing guidelines](https://github.com/UBC-MDS/pytextprep/blob/main/CONTRIBUTING.md). \n\nPlease note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`pytextprep` was created by Arijeet Chatterjee, Joshua Sia, Melisa Maidana, Philson Chan (DSCI_524_GROUP21). \n\nIt is licensed under the terms of the MIT license.\n\n## Credits\n\n`pytextprep` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Arijeet Chatterjee, Joshua Sia, Melisa Maidana, Philson Chan',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
