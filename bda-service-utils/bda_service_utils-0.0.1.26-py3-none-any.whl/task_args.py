import os
import sys
from collections import defaultdict


def get_db_url():
    """Computes sqlalchemy connection URL

    Uses the s.d.username, s.d.password and s.d.url properties to compute the sqlalchemy url.
    This provides access to the SCDF internal DB and tables such as TASK_EXECUTION.
    Returns:
      sqlalchemy compatible URL compatible with the target DB.
    """
    username = get_cmd_arg('spring.datasource.username')
    password = get_cmd_arg('spring.datasource.password')
    jdbc_url = get_cmd_arg('spring.datasource.url')

    return str(jdbc_url) \
        .replace('jdbc:', '') \
        .replace('sqlserver:', 'mssql+pyodbc:') \
        .replace('//', '//{username}:{password}@'.format(username=username, password=password))


def get_task_id():
    """Task ID as handled inside SCDF.

    When launching tasks SCDF provides the spring.cloud.task.executionid as command line argument.
    Returns:
      The task id as handled inside SCDF.
    """
    return get_cmd_arg('spring.cloud.task.executionid')


def get_task_name():
    return get_cmd_arg('spring.cloud.task.name')


def get_cmd_arg(name):
    d = defaultdict(list)
    for cmd_args in sys.argv[1:]:
        cmd_arg = cmd_args.split('=')
        if len(cmd_arg) == 2:
            d[cmd_arg[0].lstrip('-')].append(cmd_arg[1])

    if name in d:
        return d[name][0]
    else:
        print('Unknown command line arg requested: {}'.format(name))


def get_env_var(name):
    if name in os.environ:
        return os.environ[name]
    else:
        print('Unknown environment variable requested: {}'.format(name))


def get_kafka_binder_brokers():
    return get_env_var('SPRING_CLOUD_STREAM_KAFKA_BINDER_BROKERS')


def get_input_channel():
    return get_cmd_arg("spring.cloud.stream.bindings.input.destination")


def get_output_channel():
    return get_cmd_arg("spring.cloud.stream.bindings.output.destination")


def get_reverse_string():
    return get_cmd_arg("reversestring")


def get_cmd_arg(name):
    if name in get_args():
        return get_args()[name]


class AttrDict(dict):
    def __getattr__(self, name):
        return self[name]

def get_args():
    args = {}
    for _ in sys.argv[1:]:
        if "=" in _:
            p = _.split('=', 1)
            args[p[0].replace("--", "", 1)] = p[1]
    return AttrDict(args)