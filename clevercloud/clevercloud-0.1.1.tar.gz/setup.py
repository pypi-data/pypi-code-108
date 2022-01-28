# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['clevercloud']

package_data = \
{'': ['*']}

install_requires = \
['nltk>=3.6.7,<4.0.0',
 'pandas>=1.3.5,<2.0.0',
 'stem>=1.8.0,<2.0.0',
 'wordcloud>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'clevercloud',
    'version': '0.1.1',
    'description': 'A package for creating clever word clouds',
    'long_description': '# clevercloud\n\nCreating meaningful word clouds! \n\n## Summary\n\nThis package is developed to serve as the one-step solution to create meaningful and visually appealing word clouds. To create meaningful word clouds, data scientists typically takes multiple steps to clean the data, such as removing stopwords, removing punctuation and digits, making the letters lower cases, conducting lemmatization and stemming. This package will help data scientists clean the data easily following the common practices and also allow to a meaningful word cloud with customized stopwords. \n\n## Functions\n\nThere are 4 functions in this package:\n\n-   `CleverClean` A preprocessor to convert all the letters to lower case and remove punctuations.\n\n-   `CleverLemStem` A preprocessor to conduct lemmatization and stemming on the text.\n\n-   `CleverStopwords` A comprehensive list of English stopwords that allow adding more customized words.\n\n-   `CleverWordCloud` As function to generate a meaningful word cloud that allows customized stopwords. \n\n## Fitting into the Python ecosystem\n\nPackages that have similar functions:\n\n- [WordCloud](https://github.com/amueller/word_cloud): a word count generator that emphasis more frequently used words from an array of strings and represents them in the form of an image. \n\nWhat we do differently: \n\n- Our aim is to improve on the pre-processing of strings before creating a wordcloud in order to make it more user specific and efficient.\n\n- Word cloud only eliminates limited amount of stopwords, but with our package we are giving users the opportunity to add more stopwords that cater to their analysis.\n\n- We are focused on removing as many redundant and duplicate words by setting strings to lower case, removing punctuation, lemmatizing and stemming the text. \n\n\n## Installation\n\n``` bash\n$ pip install clevercloud\n```\n\n## Usage\n\n`clevercloud` can be used to preprocess text and create a meaningful word cloud with customized stopwords\nas follows:\n\n```python\nfrom clevercloud.CleverClean import CleverClean\nfrom clevercloud.CleverLemStem import CleverLemStem\nfrom clevercloud.CleverStopwords import CleverStopwords\nfrom clevercloud.CleverWordCloud import CleverWordCloud\n\nimport pandas as pd\ntext = ["is is a feet feet crying beautiful123", "maximum feet RUNNING!!", "BEAUTIFUL feet beautiful crying"]\ntest_text = pd.Series(text) # input pandas series\n\nclean_text = CleverClean(test_text)\nfinal_text = CleverLemStem(clean_text)\nnew_stopwords = CleverStopwords({"foot", "cry"})\nWordCloud = CleverWordCloud(final_text, new_stopwords, max_w=3)\n\n```\n\n## Contributing\n\nContributors of the project: Amelia Tang, Arushi Ahuja, Victor Francis, Adrianne Leung\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`clevercloud` was created by Amelia Tang, Arushi Ahuja, Victor Francis, Adrianne Leung. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`clevercloud` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Group_20',
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
