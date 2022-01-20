# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minicons', 'minicons.bin']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.5,<2.0.0',
 'polyleven>=0.7,<0.8',
 'torch>=1.8.0,<2.0.0',
 'transformers>=4.4.1,<5.0.0',
 'urllib3>=1.26.7,<2.0.0']

entry_points = \
{'console_scripts': ['minicons = minicons.bin.score_cli:process']}

setup_kwargs = {
    'name': 'minicons',
    'version': '0.2.2',
    'description': 'A package of useful functions to analyze transformer based language models.',
    'long_description': '# minicons\n\n[![Downloads](https://static.pepy.tech/personalized-badge/minicons?period=total&units=international_system&left_color=black&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/minicons)\n\nHelper functions for analyzing Transformer based representations of language\n\nThis repo is a wrapper around the `transformers` [library](https://huggingface.co/transformers) from hugging face :hugs:\n\n\n## Installation\n\nInstall from Pypi using:\n\n```pip install minicons```\n\n## Supported Functionality\n\n- Extract word representations from Contextualized Word Embeddings\n- Score sequences using language model scoring techniques, including masked language models following [Salazar et al. (2020)](https://www.aclweb.org/anthology/2020.acl-main.240.pdf).\n\n\n## Examples\n\n1. Extract word representations from contextualized word embeddings:\n\n```py\nfrom minicons import cwe\n\nmodel = cwe.CWE(\'bert-base-uncased\')\n\ncontext_words = [("I went to the bank to withdraw money.", "bank"), \n                 ("i was at the bank of the river ganga!", "bank")]\n\nprint(model.extract_representation(context_words, layer = 12))\n\n\'\'\' \ntensor([[ 0.5399, -0.2461, -0.0968,  ..., -0.4670, -0.5312, -0.0549],\n        [-0.8258, -0.4308,  0.2744,  ..., -0.5987, -0.6984,  0.2087]],\n       grad_fn=<MeanBackward1>)\n\'\'\'\n```\n\n2. Compute sentence acceptability measures (surprisals) using Word Prediction Models:\n\n```py\nfrom minicons import scorer\n\nmlm_model = scorer.MaskedLMScorer(\'bert-base-uncased\', \'cpu\')\nilm_model = scorer.IncrementalLMScorer(\'distilgpt2\', \'cpu\')\n\nstimuli = ["The keys to the cabinet are on the table.",\n           "The keys to the cabinet is on the table."]\n\n# use sequence_score with different reduction options: \n# Sequence Surprisal - lambda x: -x.sum(1)\n# Sequence Log-probability - lambda x: x.sum(1)\n# Sequence Surprisal, normalized by number of tokens - lambda x: -x.mean(1)\n# Sequence Log-probability, normalized by number of tokens - lambda x: x.mean(1)\n# and so on...\n\nprint(ilm_model.sequence_score(stimuli, reduction = lambda x: -x.sum(0).item()))\n\n\'\'\'\n[39.879737854003906, 42.75846481323242]\n\'\'\'\n\n# MLM scoring, inspired by Salazar et al., 2020\nprint(mlm_model.sequence_score(stimuli, reduction = lambda x: -x.sum(0).item()))\n\'\'\'\n[13.962685585021973, 23.415111541748047]\n\'\'\'\n```\n\n## Tutorials\n\n- [Introduction to using LM-scoring methods using minicons](https://kanishka.xyz/post/minicons-running-large-scale-behavioral-analyses-on-transformer-lms/)\n- [Computing sentence and token surprisals using minicons](examples/surprisals.md)\n- [Extracting word/phrase representations using minicons](examples/word_representations.md)\n\n## Recent Updates\n- **November 6, 2021:** MLM scoring has been fixed! You can now use `model.token_score()` and `model.sequence_score()` with `MaskedLMScorers` as well!',
    'author': 'Kanishka Misra',
    'author_email': 'kmisra@purdue.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kanishkamisra/minicons',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4',
}


setup(**setup_kwargs)
