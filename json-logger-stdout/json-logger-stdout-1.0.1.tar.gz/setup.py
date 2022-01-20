# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_logger_stdout']

package_data = \
{'': ['*']}

install_requires = \
['python-json-logger>=2.0.2,<3.0.0']

setup_kwargs = {
    'name': 'json-logger-stdout',
    'version': '1.0.1',
    'description': 'JSON Logger for MicroServices. Prints logs to the stdout of the service and can be shipped to ES by leveraging a centralized tool like Fluentd',
    'long_description': "JSON Logger for MicroServices. Prints logs to the stdout of the service and can be shipped to ES by leveraging a centralized tool like Fluentd\nUsage Examples\n`json_std_logger` is the log object that the library exports and it exposes methods for all log levels which is shown in the examples. \nNote that passing multiple arguments to the logger will print them in messages and passing named parameters to the logger will add them as extra parameters in the final log record.\n\n```\nfrom json_logger_stdout import JSONStdFormatter, json_std_logger\n\njson_std_logger.error('error log')\njson_std_logger.info('info log')\njson_std_logger.debug('debug log')\n\nimport logging\njson_std_logger.setLevel(logging.DEBUG)\njson_std_logger.debug('debug log')\n\njson_std_logger.setFormatter('%(timestamp)s %(level)s %(name) %(filename)s %(lineno)s %(module)s %(message)s')\njson_std_logger.setFormatter(None, JSONStdFormatter('%(timestamp)s %(level)s %(name) %(filename)s %(lineno)s %(module)s %(message)s'))\njson_std_logger.debug({'a': 'relates'}, {'ljlkjl': 3823}, extra='extraInfo')\n```\n",
    'author': 'Chalukya J',
    'author_email': 'chalukyaj@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/chalukyaj/json-logger-stdout',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
