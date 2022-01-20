# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autograde',
 'autograde.backend',
 'autograde.backend.container',
 'autograde.backend.local',
 'autograde.cli',
 'autograde.static']

package_data = \
{'': ['*'], 'autograde': ['templates/*']}

install_requires = \
['Flask>=2.0,<2.1',
 'Jinja2>=3.0,<3.1',
 'dataclasses-json>=0.5,<0.6',
 'django-htmlmin-ajax>=0.11,<0.12',
 'ipykernel>=6.7,<6.8',
 'jupyter>=1.0,<1.1',
 'matplotlib>=3.5,<3.6',
 'numpy>=1.22,<1.23',
 'pandas>=1.3,<1.4',
 'scipy>=1.7,<1.8',
 'seaborn>=0.11,<0.12']

entry_points = \
{'ag_backends': ['docker = autograde.backend.container:Docker',
                 'local = autograde.backend.local:Local',
                 'podman = autograde.backend.container:Podman'],
 'console_scripts': ['autograde = autograde.cli.__main__:cli']}

setup_kwargs = {
    'name': 'jupyter-autograde',
    'version': '0.4.2',
    'description': 'Unittesting & Grading of Jupyter Notebooks',
    'long_description': "# autograde\n\n[![autograde test](https://github.com/cssh-rwth/autograde/workflows/test%20autograde/badge.svg)](https://github.com/cssh-rwth/autograde/actions)\n[![autograde on PyPI](https://img.shields.io/pypi/v/jupyter-autograde?color=blue&label=jupyter-autograde)](https://pypi.org/project/jupyter-autograde)\n\n*autograde* is a toolbox for testing *Jupyter* notebooks. Its features include execution of notebooks (optionally\nisolated via docker/podman) with consecutive unit testing of the final notebook state. An audit mode allows for refining\nresults (e.g. grading plots by hand). Eventually, *autograde* can summarize these results in human and machine-readable\nformats.\n\n## setup\n\nInstall _autograde_ from _PyPI_ using _pip_ like this\n\n```shell\npip install jupyter-autograde\n```\n\nAlternatively, _autograde_ can be set up from source code by cloning this repository and installing it\nusing [poetry](https://python-poetry.org/docs/)\n\n```shell\ngit clone https://github.com/cssh-rwth/autograde.git && cd autograde\npoetry install\n```\n\nIf you intend to use autograde in a sandboxed environment\nensure [rootless docker](docs.docker.com/engine/security/rootless/) or [podman](podman.io/getting-started/installation)\nare available on your system. So far, only rootless mode is supported!\n\n## Usage\n\nOnce installed, *autograde* can be invoked via the`autograde` command. If you are using a virtual environment (which\npoetry does implicitly) you may have to activate it first. Alternative methods:\n\n- `path/to/python -m autograde` runs *autograde* with a specific python binary, e.g. the one of your virtual\n  environment.\n- `poetry run autograde` if you've installed *autograde* from source\n\nTo get an overview over all options available, run\n\n```shell\nautograde [sub command] --help\n```\n\n### Testing\n\n*autograde* comes with some example files located in the `demo/`\nsubdirectory that we will use for now to illustrate the workflow. Run\n\n```shell\nautograde test demo/test.py demo/notebook.ipynb --target /tmp --context demo/context\n```\n\nWhat happened? Let's first have a look at the arguments of *autograde*:\n\n- `demo/test.py` a script with test cases we want to apply\n- `demo/notebook.ipynb` is the a notebook to be tested (here you may also specify a directory to be recursively searched\n  for notebooks)\n- The optional flag `--target` tells *autograde* where to store results, `/tmp` in our case, and the current working\n  directory by default.\n- The optional flag `--context` specifies a directory that is mounted into the sandbox and may contain arbitrary files\n  or subdirectories. This is useful when the notebook expects some external files to be present such as data sets.\n\nThe output is a compressed archive that is named something like\n`results-Member1Member2Member3-XXXXXXXXXX.zip` and which has the following contents:\n\n- `artifacts/`: directory with all files that where created or modified by the tested notebook as well as rendered\n  matplotlib plots.\n- `code.py`: code extracted from the notebook including\n  `stdout`/`stderr` as comments\n- `notebook.ipynb`: an identical copy of the tested notebook\n- `restults.json`: test results\n\n### Audit Mode\n\nThe interactive audit mode allows for manual refining the result files. This is useful for grading parts that cannot be\ntested automatically such as plots or text comments.\n\n```shell\nautograde audit path/to/results\n```\n\n**Overview**\n[![autograde on PyPI](assets/overview.png)](assets/overview.png)\n\n**Auditing**\n[![autograde on PyPI](assets/audit.png)](assets/audit.png)\n\n**Report Preview**\n[![autograde on PyPI](assets/report.png)](assets/report.png)\n\n### Generate Reports\n\nThe `report` sub command creates human readable HTML reports from test results:\n\n```shell\nautograde report path/to/result(s)\n```\n\nThe report is added to the results archive inplace.\n\n### Patch Result Archives\n\nResults from multiple test runs can be merged via the `patch` sub command:\n\n```shell\nautograde patch path/to/result(s) /path/to/patch/result(s)\n```\n\n### Summarize Multiple Results\n\nIn a typical scenario, test cases are not just applied to one notebook but many at a time. Therefore, *autograde* comes\nwith a summary feature, that aggregates results, shows you a score distribution and has some very basic fraud detection.\nTo create a summary, simply run:\n\n```shell\nautograde summary path/to/results\n```\n\nTwo new files will appear in the result directory:\n\n- `summary.csv`: aggregated results\n- `summary.html`: human readable summary report\n\n## Snippets\n\n**Work with result archives programmatically**\n\nFix score for a test case in all result archives:\n\n```python\nfrom pathlib import Path\n\nfrom autograde.backend.local.util import find_archives, traverse_archives\n\n\ndef fix_test(path: Path, faulty_test_id: str, new_score: float):\n    for archive in traverse_archives(find_archives(path), mode='a'):\n        results = archive.results.copy()\n        for faulty_test in filter(lambda t: t.id == faulty_test_id, results.unit_test_results):\n            faulty_test.score_max = new_score\n            archive.inject_patch(results)\n\n\nfix_test(Path('...'), '...', 13.37)\n```\n\n**Special Test Cases**\n\nEnsure a student id occurs at most once:\n\n```python\nfrom collections import Counter\n\nfrom autograde import NotebookTest\n\nnbt = NotebookTest('demo notebook test')\n\n\n@nbt.register(target='__TEAM_MEMBERS__', label='check for duplicate student id')\ndef test_special_variables(team_members):\n    id_counts = Counter(member.student_id for member in team_members)\n    duplicates = {student_id for student_id, count in id_counts.items() if count > 1}\n    assert not duplicates, f'multiple members share same id ({duplicates})'\n```\n\n\n",
    'author': 'Lukas Ochse',
    'author_email': None,
    'maintainer': 'Chair for Computational Social Sciences and Humanities at RWTH Aachen University',
    'maintainer_email': None,
    'url': 'https://github.com/cssh-rwth/autograde',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
