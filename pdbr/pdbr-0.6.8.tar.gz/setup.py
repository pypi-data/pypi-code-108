# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pdbr', 'pdbr.middlewares']

package_data = \
{'': ['*']}

install_requires = \
['icecream>=2.1.0,<3.0.0', 'rich>=10.0.0,<11.0.0', 'sqlparse>=0.4.2,<0.5.0']

extras_require = \
{':extra == "ipython"': ['jedi==0.17.2'],
 ':sys_platform == "win32"': ['pyreadline>=2.1,<3.0'],
 'celery': ['celery>=5.2.2,<6.0.0'],
 'ipython': ['ipython==7.16.3']}

entry_points = \
{'console_scripts': ['pdbr = pdbr.cli:shell', 'pdbr_telnet = pdbr.cli:telnet']}

setup_kwargs = {
    'name': 'pdbr',
    'version': '0.6.8',
    'description': 'Pdb with Rich library.',
    'long_description': '# pdbr\n\n[![PyPI version](https://badge.fury.io/py/pdbr.svg)](https://pypi.org/project/pdbr/) [![Python Version](https://img.shields.io/pypi/pyversions/pdbr.svg)](https://pypi.org/project/pdbr/) [![](https://github.com/cansarigol/pdbr/workflows/Test/badge.svg)](https://github.com/cansarigol/pdbr/actions?query=workflow%3ATest) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/cansarigol/pdbr/master.svg)](https://results.pre-commit.ci/latest/github/cansarigol/pdbr/master)\n\n\npdbr is intended to make the PDB results more colorful. it uses [Rich](https://github.com/willmcgugan/rich) library to carry out that.\n\n\n## Installing\n\nInstall with `pip` or your favorite PyPi package manager.\n\n```\npip install pdbr\n```\n\n\n## Breakpoint\n\nIn order to use ```breakpoint()```, set **PYTHONBREAKPOINT** with "pdbr.set_trace"\n\n```python\nimport os\n\nos.environ["PYTHONBREAKPOINT"] = "pdbr.set_trace"\n```\n\nor just import pdbr\n\n```python\nimport pdbr\n```\n\n## New commands\n### (ic)ecream\n🍦 [Icecream](https://github.com/gruns/icecream) print.\n### (i)nspect / inspectall | ia\n[rich.inspect](https://rich.readthedocs.io/en/latest/introduction.html?s=03#rich-inspector)\n### search | src\nSearch a phrase in the current frame.\nIn order to repeat the last one, type **/** character as arg.\n### sql\nDisplay value in sql format.\n![](/images/image13.png)\n\nIt can be used for Django model queries as follows.\n```\n>>> sql str(Users.objects.all().query)\n```\n![](/images/image14.png)\n### (syn)tax\n[ val,lexer ] Display [lexer](https://pygments.org/docs/lexers/).\n### (v)ars\nGet the local variables list as table.\n### varstree | vt\nGet the local variables list as tree.\n\n![](/images/image5.png)\n\n## Config\n### Style\nIn order to use Rich\'s traceback, style, and theme, set **setup.cfg**.\n\n```\n[pdbr]\nstyle = yellow\nuse_traceback = True\ntheme = friendly\n```\n\n### History\n**store_history** setting is used to keep and reload history, even the prompt is closed and opened again.\n```\n[pdbr]\n...\nstore_history=.pdbr_history\n```\n\n## Celery\nIn order to use **Celery** remote debugger with pdbr, use ```celery_set_trace``` as below sample. For more information see the [Celery user guide](https://docs.celeryproject.org/en/stable/userguide/debugging.html).\n\n```python\nfrom celery import Celery\n\napp = Celery(\'tasks\', broker=\'pyamqp://guest@localhost//\')\n\n@app.task\ndef add(x, y):\n\n    import pdbr; pdbr.celery_set_trace()\n\n    return x + y\n\n```\n#### Telnet\nInstead of using `telnet` or `nc`, in terms of using pdbr style, `pdbr_telnet` command can be used.\n![](/images/image6.png)\n\nAlso in order to activate history and be able to use arrow keys, install and use [rlwrap](https://github.com/hanslub42/rlwrap) package.\n\n```\nrlwrap -H \'~/.pdbr_history\' pdbr_telnet localhost 6899\n```\n\n## IPython\n\nBeing able to use [ipython](https://ipython.readthedocs.io/), install pdbr with it like below or just install your own version.\n\n```\npip install pdbr[ipython]\n```\n\n## pytest\nIn order to use `pdbr` with pytest `--pdb` flag, add `addopts` setting in your pytest.ini.\n\n```\n[pytest]\naddopts: --pdbcls=pdbr:RichPdb\n```\n## Context Decorator\n`pdbr_context` and `apdbr_context` (`asyncio` corresponding) can be used as **with statement** or **decorator**. It calls `post_mortem` if `traceback` is not none.\n\n```python\nfrom pdbr import apdbr_context, pdbr_context\n\n@pdbr_context()\ndef foo():\n    ...\n\ndef bar():\n    with pdbr_context():\n        ...\n\n\n@apdbr_context()\nasync def foo():\n    ...\n\nasync def bar():\n    async with apdbr_context():\n        ...\n```\n\n![](/images/image12.png)\n## Django DiscoverRunner\nTo being activated the pdb in Django test, change `TEST_RUNNER` like below. Unlike Django (since you are not allowed to use for smaller versions than 3), pdbr runner can be used for version 1.8 and subsequent versions.\n\n```\nTEST_RUNNER = "pdbr.runner.PdbrDiscoverRunner"\n```\n![](/images/image10.png)\n## Middlewares\n### Starlette\n```python\nfrom fastapi import FastAPI\nfrom pdbr.middlewares.starlette import PdbrMiddleware\n\napp = FastAPI()\n\napp.add_middleware(PdbrMiddleware, debug=True)\n\n\n@app.get("/")\nasync def main():\n    1 / 0\n    return {"message": "Hello World"}\n```\n### Django\nIn order to catch the problematic codes with post mortem, place the middleware class.\n\n```\nMIDDLEWARE = (\n    ...\n    "pdbr.middlewares.django.PdbrMiddleware",\n)\n```\n![](/images/image11.png)\n## Shell\nRunning `pdbr` command in terminal starts an `IPython` terminal app instance. Unlike default `TerminalInteractiveShell`, the new shell uses pdbr as debugger class instead of `ipdb`.\n#### %debug magic sample\n![](/images/image9.png)\n### Terminal\n#### Django shell sample\n![](/images/image7.png)\n\n## Vscode user snippet\n\nTo create or edit your own snippets, select **User Snippets** under **File > Preferences** (**Code > Preferences** on macOS), and then select **python.json**.\n\nPlace the below snippet in json file for **pdbr**.\n\n```\n{\n  ...\n  "pdbr": {\n        "prefix": "pdbr",\n        "body": "import pdbr; pdbr.set_trace()",\n        "description": "Code snippet for pdbr debug"\n    },\n}\n```\n\nFor **Celery** debug.\n\n```\n{\n  ...\n  "rdbr": {\n        "prefix": "rdbr",\n        "body": "import pdbr; pdbr.celery_set_trace()",\n        "description": "Code snippet for Celery pdbr debug"\n    },\n}\n```\n\n## Samples\n![](/images/image1.png)\n\n![](/images/image3.png)\n\n![](/images/image4.png)\n\n### Traceback\n![](/images/image2.png)\n',
    'author': 'Can Sarigol',
    'author_email': 'ertugrulsarigol@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cansarigol/pdbr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.12,<4.0.0',
}


setup(**setup_kwargs)
