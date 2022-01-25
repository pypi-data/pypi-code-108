import logging
import sys
import traceback
import re
import logs.config_server_log
import logs.config_client_log

if sys.argv[0].find('client_file') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client_file')

def log(func_to_log):
    """
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию о имени вызываемой функиции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    """

    def log_saver(*args,**kwargs):
        ret = func_to_log(*args,**kwargs)
        name_of_component = re.split(r'\\|"',traceback.format_stack()[0].split(",")[0])[-2]
        LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} с параметрами {args}, {kwargs}.'
                     f'Вызов из модуля {func_to_log.__module__}.'
                     f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]} компонента {name_of_component}')
        return ret
    return log_saver