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
    'version': '1.0.3',
    'description': 'JSON Logger for MicroServices. Prints logs to the stdout of the service and can be shipped to ES by leveraging a centralized tool like Fluentd.',
    'long_description': '# JSON Logger Stdout\n##### Log to the stdout directly so that they can be consumed by some centralized log collecting service like Fluentd.\n=================================================================================================\n\nJSON Logger for MicroServices. Prints logs to the stdout of the service and can be shipped to ES by leveraging a centralized tool like Fluentd\n> Usage Examples\n`json_std_logger` is the log object that the library exports and it exposes methods for all log levels which is shown in the examples.\n\n> Important Note: By default the log level is set at `INFO`. Please change it using the `setLevel` method which is exposed out.\n\n\n```bash\nfrom json_logger_stdout import JSONStdFormatter, json_std_logger\n\n#By Default the log level is INFO\n\njson_std_logger.error(\'error log\')      # {"timestamp": "2022-01-21T06:36:32.668292Z", "level": "ERROR", "message": "error log"}\njson_std_logger.info(\'info log\')        # {"timestamp": "2022-01-21T06:36:32.668420Z", "level": "INFO", "message": "info log"}\njson_std_logger.debug(\'debug log, no print\')      # Prints Nothing as the current level by default is INFO\n\nimport logging\njson_std_logger.setLevel(logging.DEBUG) # Set Log Level\njson_std_logger.debug(\'debug log\')      # {"timestamp": "2022-01-21T06:36:32.668476Z", "level": "DEBUG", "message": "debug log"}\n\n```\n\n### List of Exposed Methods\n`getLogger` : Returns the already initialized log object.\n\n`setLevel` : Sets Log Level. Pass any valid log level from the python `logging` module.\n\n`setFormatter` : Sets a custom log formatter if needed. This call will clear out all the other handlers, so please call this before adding more log handlers. It takes two arguments, the first one is simply a string that takes the fields to print in the final log. See `#Example-Set-Formatter-1` for more details.\nIt is possible to use a different log formatter altogether and use the second parameter to pass the log formatter object. See `#Example-Set-Formatter-2` for more details.\n\n`addHandlers` : Pass an array of log handlers that will be attached to the log object.\n\n### Advanced Usage\nThe package exposes two classes `JSONLoggerStdout` & `JSONStdFormatter`\nIt is possible for the user to get a different log object by using the base class `JSONLoggerStdout`\n```\njson_logger = JSONLoggerStdout(loggerName=<optional>)\n```\n\n> NOTE : All the unnamed parameters that are passed to the logger would be converted to string and concatenated with a space ` `.\nHowever sending named parameters to the logger would add the keys as extra parameters in the log record. Please see the last example for more clarity on this.\n```bash\njson_std_logger.setFormatter(\'%(timestamp)s %(level)s %(name) %(filename)s %(lineno)s %(module)s %(message)s\')     # Example-Set-Formatter-1\njson_std_logger.setFormatter(None, JSONStdFormatter(\'%(timestamp)s %(level)s %(name) %(filename)s %(lineno)s %(message)s\'))   # Example-Set-Formatter-2\n\n# Usage with variable parameters and named parameters to the logger.\njson_std_logger.debug({\'unnamedObjKey1\': \'will print in message\'}, {\'unnamedObjKey2\': \'should be concatenated with the previous part\'}, extra=\'Named Parameter, so will be addded as an extra parameter\')\n# {"timestamp": "2022-01-21T07:40:03.363500Z", "level": "DEBUG", "name": "root", "filename": "json_logger_stdout.py", "lineno": 67, "module": "json_logger_stdout", "message": "{\'unnamedObjKey1\': \'will print in message\'}, {\'unnamedObjKey2\': \'should be concatenated with the previous part\'}", "extra": "Named Parameter, so will be addded as an extra parameter"}\n```\n',
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
