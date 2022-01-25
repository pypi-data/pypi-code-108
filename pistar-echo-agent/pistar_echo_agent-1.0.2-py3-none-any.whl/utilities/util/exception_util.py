"""
description: this module provides the function trace exception.
"""
import os
from pistar_echo_agent.utilities.constants import ENCODE
from pistar_echo_agent.utilities.constants import FILE_MODE


def trace_error(index, traceback):
    """
    description: this function is used to return traceback message.
    """

    file_name = traceback.tb_frame.f_code.co_filename
    line_number = traceback.tb_frame.f_lineno
    function_name = traceback.tb_frame.f_code.co_name

    if os.path.isfile(file_name):
        with open(file_name, FILE_MODE.READ, encoding=ENCODE.UTF8) as file:
            code = file.readlines()[line_number - 1].strip()

        text = (
            '\tFile: \"{file_name}:{line_number}\" in function \"{function_name}\"\n\t  {code}'
        ).format(
            file_name=file_name,
            line_number=line_number,
            function_name=function_name,
            code=code
        )
    else:
        code = ''
        text = 'trace exception {index}:'.format(index=index)

    message = dict(
        text=text,
        file_name=file_name,
        line_number=line_number,
        code=code
    )
    return message


def trace_exception(exception, logger):
    """
    description: this function is used to trace the exception,
                 and output into the logger.
    """
    traceback = exception.__traceback__
    index = 0
    error_message = "\n  Traceback (most recent call last):\n"
    while True:
        index += 1
        traceback = traceback.tb_next
        if traceback is None:
            break

        message = trace_error(index=index, traceback=traceback)
        error_message = error_message + message['text']
        if traceback.tb_next is not None:
            error_message = error_message + "\n"
    error_message += "\n" + str(exception)
    logger.error(error_message)
