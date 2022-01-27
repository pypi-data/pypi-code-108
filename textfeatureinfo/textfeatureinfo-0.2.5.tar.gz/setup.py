# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['textfeatureinfo']

package_data = \
{'': ['*']}

install_requires = \
['nltk>=3.6.7,<4.0.0']

setup_kwargs = {
    'name': 'textfeatureinfo',
    'version': '0.2.5',
    'description': 'Package to extract interesting details about text.',
    'long_description': '# textfeatureinfo\n\n[![Documentation Status](https://readthedocs.org/projects/textfeatureinfo/badge/?version=latest)](https://textfeatureinfo.readthedocs.io/en/latest/?badge=latest) \n[![ci-cd](https://github.com/UBC-MDS/textfeatureinfo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/textfeatureinfo/actions/workflows/ci-cd.yml)\n[![codecov](https://codecov.io/gh/UBC-MDS/textfeatureinfo/branch/master/graph/badge.svg?token=P29ZWp0Oib)](https://codecov.io/gh/UBC-MDS/textfeatureinfo)\n\n\n## **Description**\n\n\nIn Natural Language Processing, it is common for users to try and engineer their own features from a given text. It can be difficult to extract certain features from text without using additional Python tools. This python package includes functions that allows data scientists to extract information from text features which can be useful for feature engineering, or in other data science projects. Our package, textfeatureinfo, will help gather summary information from plain text such as the number of punctuations in the text, the average word lengths and the percentage of fully capitalised words which can be useful information for feature engineering. Additionally, our package can also manipulate text data by removing the stopwords for the ease of future processing steps. \n\nOur package and functions are inspired from a lab in the course, DSCI 573 (Feature and model selection), of UBC MDS program, and are tailored based on our own experience and interest. \n\n## **Function Details**\n\n- `count_punc`: This function will count and return the number of punctuations within a given text.\n- `avg_word_len`: This function will calculate and return the average length of words within a given text.\n- `perc_cap_words`: This function will calculate the percentage of fully capitalised words in the text.\n- `remove_stop_words`: This function will find and remove the stop words in a text and will return the list of clean words.\n\n## **Python Ecosystem**\n\nIn the field of text feature engineering, we are cognisant that there are well established packages in the Python ecosystem - specifically [`nltk`](https://www.nltk.org/), [`SpaCy`](https://stackabuse.com/removing-stop-words-from-strings-in-python/#usingthespacylibrary) and [`genism`](https://radimrehurek.com/gensim/). For punctuations, we are aware that the [`nltk.tokenize`](https://www.nltk.org/api/nltk.tokenize.html) and [`nltk.probability: FreqDist`](https://www.kite.com/python/docs/nltk.FreqDist) package can be used to find the number of words and punctuations in a string. To calculate average word length, [`nltk.word_tokenize()`](https://www.nltk.org/api/nltk.tokenize.html) is able to divide strings into lists of substrings. To count the number of fully capitalised words in a text, the above functions do provide a means to isolate these characters, but not to count them explicitly. In the case of stop words, there are several modules that identify stop words. For instance, `genius.parsing.preprocessing` module has the function `remove_stopwords()` which allows users to remove specific stop words, as listed in their docstring from a string. `nltk.corpus` has a module [`stopwords`](https://www.geeksforgeeks.org/removing-stop-words-nltk-python/) to remove stop words from the `text_token` list. The package `SpaCy` similarly has a list of stopwords stored in `sp.Default.stop_words` in English. \n\nBased on our experience in our previous module, all the functions that we seek to use require several lines of code. For example, to calculate the average word length, we need to extract the punctuation, count total number of characters, then averaging out over the number of words present. As such, we seek to simplify these tasks into functions that users, including ourselves, can employ in one line of code. \n\n\n## Installation\n\n```bash\n$ pip install textfeatureinfo\n```\n\n## Usage\n\nIn order to use the package please go through the following steps:\n\n1. Create a new conda environment:\n\n```bash\nconda create --name textfeatureinfo python=3.9 -y\n```\n\n2. Activate the conda environment:\n\n```bash\nconda activate textfeatureinfo\n```\n\n3. Install the package:\n\n```bash\npip install textfeatureinfo\n```\n\n4. Open Python:\n\n```bash\npython\n```\n\n5. In the Python prompt type the following:\n\n```bash\n>>> from textfeatureinfo import textfeatureinfo\n>>> from textfeatureinfo.textfeatureinfo import count_punc\n>>> from textfeatureinfo.textfeatureinfo import avg_word_len\n>>> from textfeatureinfo.textfeatureinfo import perc_cap_words\n>>> from textfeatureinfo.textfeatureinfo import remove_stop_words\n```\n\nNow you can use the functions.\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`textfeatureinfo` was created by Kiran, Jacqueline, Paniz, Lynn. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`textfeatureinfo` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Kiran, Jacqueline, Paniz, Lynn',
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
