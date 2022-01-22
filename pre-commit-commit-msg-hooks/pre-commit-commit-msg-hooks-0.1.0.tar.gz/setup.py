# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pre_commit_commit_msg_hooks']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['check-description-max-length = '
                     'pre_commit_commit_msg_hooks.check_description_max_length:main',
                     'check-second-line-empty = '
                     'pre_commit_commit_msg_hooks.check_second_line_empty:main',
                     'check-summary-capitalized = '
                     'pre_commit_commit_msg_hooks.check_summary_capitalized:main',
                     'check-summary-conjunction = '
                     'pre_commit_commit_msg_hooks.check_summary_conjunction:main',
                     'check-summary-imperative = '
                     'pre_commit_commit_msg_hooks.check_summary_imperative:main',
                     'check-summary-max-length = '
                     'pre_commit_commit_msg_hooks.check_summary_max_length:main',
                     'check-summary-min-length = '
                     'pre_commit_commit_msg_hooks.check_summary_min_length:main',
                     'check-summary-punctuation = '
                     'pre_commit_commit_msg_hooks.check_summary_punctuation:main']}

setup_kwargs = {
    'name': 'pre-commit-commit-msg-hooks',
    'version': '0.1.0',
    'description': 'A collection of checks for the commit-msg for pre-commit.',
    'long_description': '###########################\npre-commit-commit-msg-hooks\n###########################\n\nA collection of checks for the commit-msg for pre-commit.\n\nThe hooks in this repository makes it possible to check for the\nrules defined by https://commit.style/.::\n\n   Commit message style guide for Git\n\n   The first line of a commit message serves as a summary.  When displayed\n   on the web, it\'s often styled as a heading, and in emails, it\'s\n   typically used as the subject.  As such, you should capitalize it and\n   omit any trailing punctuation.  Aim for about 50 characters, give or\n   take, otherwise it may be painfully truncated in some contexts.  Write\n   it, along with the rest of your message, in the imperative tense: "Fix\n   bug" and not "Fixed bug" or "Fixes bug".  Consistent wording makes it\n   easier to mentally process a list of commits.\n\n   Oftentimes a subject by itself is sufficient.  When it\'s not, add a\n   blank line (this is important) followed by one or more paragraphs hard\n   wrapped to 72 characters.  Git is strongly opinionated that the author\n   is responsible for line breaks; if you omit them, command line tooling\n   will show it as one extremely long unwrapped line.  Fortunately, most\n   text editors are capable of automating this.\n\n   :q\n\n\nAnd then some.\n\nAll hooks can be used from the command line as well.\n\nUsage\n=====\nConfigure https://pre-commit.com for checking compliance with\nhttps://commit.style\n\n.. code-block::\n    :name: .pre-commit-config.yaml\n\n    repos:\n      - repo: ../pre-commit-commit-msg-hooks\n        rev: 0.1.0\n        hooks:\n          - id: check-description-max-length\n          - id: check-second-line-empty\n          - id: check-summary-capitalized\n          - id: check-summary-imperative\n          - id: check-summary-max-length\n          - id: check-summary-punctuation\n\n\nAvailable Hooks\n===============\n\ncheck-description-max-length\n----------------------------\n\nCheck lines in the description are not more than 72 characters.\n\n\ncheck-second-line-empty\n-----------------------\n\nCheck the second line of the commit message is blank.\n\n\ncheck-summary-conjunction\n-------------------------\n\nCheck the summary does not contain conjugated sentences.\n\nSearches for occurrences of \'and\', \'nor\', and \'or\' and fails if found.\n\n\ncheck-summary-imperative\n------------------------\n\nCheck the summary starts with a verb.\n\nSearches a wordlist comprised of > 6000 verbs. The check fails\nif not found.\n\n.. note::\n    The wordlist is comprised of different lists but as terminology\n    evolves, the list is incomplete. If you find anything missing,\n    please amend `verbs-wordlist.txt <https://github.com/rlindsgaard/\n    pre-commit-commit-msg-hooks/blob/master/pre_commit_commit_msg_hooks/\n    verbs-wordlist.txt>`_\n    and issue a Pull Request.\n\n\ncheck-summary-capitalized\n-------------------------\n\nCheck the summary starts with a capital letter.\n\n\ncheck-summary-max-length\n------------------------\n\nCheck the summary is not more than 54 characters.\n\n.. note::\n    https://commit.style says `Aim for about 50 characters, give\n    or take`. 54 gives a little more lee-way.\n\n\ncheck-summary-min-length\n------------------------\n\nCheck the summary is at least 6 characters.\n\n\ncheck-summary-punctuation\n-------------------------\n\nCheck the summary does not end with punctuation.\n\nChecks the last character against `string.punctuation\n<https://docs.python.org/3/library/string.html#string.punctuation>`_\nand fails on match.\n',
    'author': 'Ronni Elken Lindsgaard',
    'author_email': 'ronni.lindsgaard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rlindsgaard/pre-commit-commit-msg-hooks',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
