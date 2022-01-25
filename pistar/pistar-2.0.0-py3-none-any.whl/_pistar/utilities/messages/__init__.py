"""
description: this module provides messages of pistar.
"""


def call_begin(function_name, parameters=None):
    """
    description: at the beginning of the function, show this message.
    """
    if parameters:
        return f'>>> function \'{function_name}\' is calling, with parameters {parameters}'
    else:
        return f'>>> function \'{function_name}\' is calling'


def call_successfully(function_name):
    """
    description: if the function is called call_successfully,
                 show this message.
    """
    return f'<<< function \'{function_name}\' is called successfully'


def call_failed(function_name, exception):
    """
    description: if the function is called failed, show this message.
    """
    return f'<<< function \'{function_name}\' is called failed, {exception}'
