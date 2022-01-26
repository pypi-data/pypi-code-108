# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['make_runner']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['mrun = make_runner.run:main']}

setup_kwargs = {
    'name': 'make-runner',
    'version': '0.2.1',
    'description': 'Enhanced Makefile-based task runner',
    'long_description': '.. image:: https://user-images.githubusercontent.com/12455831/122683398-cd0bbf00-d239-11eb-95cc-39a1bf911224.png\n   :alt: banner\n\nInstallation\n############\nYou can install via pip.\n\n::\n\n   pip install make-runner\n\nUsage\n#####\nAll you have to do is add a comment starting with :code:`##` to your Makefile.\nThe comment should be added to the end of line of PHONY targets and the above line of constant settings.\n\n.. code-block:: makefile\n\n   ## source filename\n   SRC_FILE := source.txt\n   ## target filename\n   TGT_FILE := target.txt\n\n   $(TGT_FILE): $(SRC_FILE)\n        cp $(SRC_FILE) $(TGT_FILE)\n\n   .PHONY: copy\n   copy: $(TGT_FILE) ## copy a file from SRC_FILE to TGT_FILE\n\n\nThen, type :code:`mrun` in the same directory as your Makefile.\n\n.. image:: https://github.com/de9uch1/make-runner/blob/master/example/mrun.png\n   :alt: screenshot\n',
    'author': 'Hiroyuki Deguchi',
    'author_email': 'deguchi.hiroyuki.db0@is.naist.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/de9uch1/make-runner',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
