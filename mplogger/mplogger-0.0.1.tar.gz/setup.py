# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mplogger']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mplogger',
    'version': '0.0.1',
    'description': 'Multi-processing capable print-like logger for Python',
    'long_description': "# MPLogger\nMulti-processing capable print-like logger for Python\n\n## Requirements and Installation\n\nPython 3.8+ is required\n\n### Pip\n\n`pip install mplogger`\n\n### Manual\n\n[_Poetry_](https://python-poetry.org/) and (optionally) [_GNU Make_](https://www.gnu.org/software/make/) are required.\n\n1. `git clone https://github.com/ELTE-DH/webarticlecurator.git`\n2. Run `make`\n\nOn Windows or without Make (after cloning the repository):\n\n1. `poetry install --no-root`\n2. `poetry build`\n3. `poetry run pip install --upgrade dist/*.whl` (the correct filename must be specified on Windows)\n\n## Usage\n\n### Single-process\n\n```python\nfrom MLPlogger import Logger\n\n# Initialize logger (default: STDERR only with INFO level)\nlogger = Logger(log_filename, logfile_mode, logfile_encoding, logfile_level, console_stream, console_level, console_format, file_format)\n\nlogger.log('INFO', 'First argument log level as string')\nlogger.log('WARNING', 'THIS IS A WARNING!', 'In multiple lines', 'just like print()', sep='\\n')\nlogger.log('CRITICAL', 'Can also set line endings!', end='\\r\\n')\n```\n\n### Multi-process\n\n```python\nfrom itertools import repeat\nfrom multiprocessing import Pool, Manager, current_process\n\nfrom MLPlogger import Logger\n\ndef worker_process(par):\n    state, lq = par\n    retl = []\n    for n in range(100):\n        lq.log('WARNING', f'{current_process().name} message{state} {n}')\n    lq.log('WARNING', f'{current_process().name} finished')\n    return retl\n\nlog_obj = Logger('test.log', 'w')  # Apply all parameters for logger here!\nlog_obj.log('INFO', 'NORMAL LOG BEGIN')  # Normal logging\nwith Manager() as man:\n    log_queue = man.Queue()\n    with log_obj.init_mp_logging_context(log_queue) as mplogger, Pool() as p:\n        # Here one can log parallel from all processes!\n        return_queue = p.imap(worker_process, zip(range(10), repeat(mplogger)), chunksize=3)\n        for _ in return_queue:\n            pass\nlog_obj.log('INFO', 'NORMAL LOG END')  # Normal logging\n```\n\n# Licence\n\nThis project is licensed under the terms of the GNU LGPL 3.0 license.\n",
    'author': 'dlazesz',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ELTE-DH/MPLogger',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
