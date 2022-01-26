# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_file_logger']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'simple-file-logger',
    'version': '0.1.5',
    'description': 'A simple logger class to log to files',
    'long_description': '# Simple File Logger\n\nThis python package provides a `Logger` class which is easy to use\nfor basic logging to files.\n\n## Install\n\n```sh\npip install simple-file-logger\n```\n\n## Usage\n\n```py\nfrom simple_file_logger import Logger\n\nlogger = Logger("my_log_file", "path/to/log/directory")\nlogger.info("Hello!")\n\n# writes to `my_log_file_YYYYMMDD_HHMM_SS.log`\n# 2022-01-26 11:57:14,182 - INFO - Hello!\n```\n\nThe constructor provides various options to configure the logger.\n\n```py\nlogfile_name: str,\nlog_dir: Union[Path, str, None]=None,\nlevel=logging.DEBUG,\nmode="w",\nadd_timestamp_to_filename=True,\nis_console_only=False,\nis_null_handler=False,\nis_rolling_handler=False,\nprocess: str = None,\n```\n\n- To create a console-only handler, pass an empty string for the first argument, and set `is_console_only` to `True`.\n- The `is_rolling_handler` parameter controls whether the logger automatically writes to a new file when the existing one becomes larger than `5mb`. It will archive the current log with a serial number and transition to a new file automatically. The limit of archived files is `5` so the oldest one will get deleted when archiving for the 6th time.\n- The `is_null_handler` parameter initializes a logger that does nothing. This is useful for unit testing libraries where functions log messages but you don\'t want any actual logging to take place.\n- The `process` parameter is a little addition to provide some info about what process the currently running script represents. It can be any arbitrary string, such as `downloading_data` or `monitoring_files` etc. This process will also appear on each log line. As the script executes, you can set the `process` in the logger object to a new value. This is helpful for producing files which facilitate easy line extraction related to a specific process when the file is big.\n\n  ```py\n  logger.process = "downloading_file"\n  # ... logic to download some file which does some logging.\n  # The lines will have `downloading_file` before the log message.\n\n  # update file contents\n  logger.process = "update_contents"  # set process to indicate the context of log messages to follow\n\n  # ... logic to update file contents and do some logging.\n\n  # no need for further process logs, and just want to log messages.\n  logger.process = ""  # prevents addition of process string to log message.\n\n  ```\n',
    'author': 'Karanveer Singh',
    'author_email': 'karan_4496@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/karanveersp/simple-file-logger',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
