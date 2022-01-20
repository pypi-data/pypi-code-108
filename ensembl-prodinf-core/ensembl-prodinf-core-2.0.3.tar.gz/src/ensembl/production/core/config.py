#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import re
import os
import logging
import yaml

logger = logging.getLogger(__name__)


def load_config_yaml(file_path, strict=False, tag='!ENV'):
    """
    Load a yaml configuration file and resolve any environment variables
    The environment variables must have !ENV before them and be in this format
    to be parsed: ${VAR_NAME}.
    E.g.:
    database:
        host: !ENV ${HOST}
        port: !ENV ${PORT}
    app:
        log_path: !ENV '/var/${LOG_PATH}'
        something_else: !ENV '${AWESOME_ENV_VAR}/var/${A_SECOND_AWESOME_VAR}'
    :param strict: String yaml loading
    :param str file_path: the path to the yaml file
    :param str tag: the tag to look for
    :return: the dict configuration
    :rtype: dict[str, T]
    See https://gist.github.com/mkaranasou/ba83e25c835a8f7629e34dd7ede01931#file-python_yaml_environment_variables-py
    """
    pattern = re.compile(r'.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !ENV somestring${MYENVVAR}blah blah blah
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):
        """
        Extracts the environment variable from the node's value
        :param yaml.Loader loader: the yaml loader
        :param node: the current node in the yaml
        :return: the parsed string that contains the value of the environment
        variable
        """
        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.environ.get(g, g)
                )
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)

    if file_path:
        with open(file_path, 'r') as f:
            config = yaml.load(f, Loader=loader)
        return config if config else {}
    else:
        if strict:
            raise ValueError('Invalid config file path: %s' % file_path)
        else:
            logger.warning('Using default configuration. Config file path was: %s', file_path)
            return {}


def parse_debug_var(var):
    return not ((str(var).lower() in ('f', 'false', 'no', 'none')) or (not var))


def load_config_json(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config if config else {}
