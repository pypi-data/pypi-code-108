import os
import re
import urllib.parse


def prepare_sql_data(data):
    sql_data = {
        'query': data['args'][data['config']['argsIndex']],
        'poSessionId': data['result']
    }

    return sql_data


def prepare_lfi_data(data):
    lfi_data = {
        'mode': 'write' if 'w' in data['args'][data['config']['argsIndex']+1] else 'read',
        'path': data['args'][data['config']['argsIndex']],
        'realpath': os.path.realpath(data['args'][data['config']['argsIndex']]),
        'poSessionId': data['result']
    }
    return lfi_data


def prepare_shellShock_data(data):
    shellShock_data = {
        'command': data['args'][data['config']['argsIndex']],
        'poSessionId': data['result']
    }

    return shellShock_data


def prepare_SSRF_data(data):
    if len(data['args']) == 2:
        return {
            'url': data['args'][data['config']['argsIndex']+1],
            'poSessionId': data['result']
        }

    return {
        'url': data['args'][data['config']['argsIndex']],
        'poSessionId': data['result']
    }
