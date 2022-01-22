import functools
import logging
import traceback


class Log:
    """ Декоратор, выполняющий логирование вызовов функций. Сохраняет события типа debug, содержащие
        информацию о имени вызываемой функиции, параметры с которыми вызывается функция, и модуль, вызывающий функцию.

    """
    def __call__(self, func_to_log):
        @functools.wraps(func_to_log)
        def decorated(*args, **kwargs):
            if traceback.format_stack()[0].strip().split()[-1].find('server') == -1:
                LOGGER = logging.getLogger('client')
            else:
                LOGGER = logging.getLogger('server')
            res = func_to_log(*args, **kwargs)
            LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {func_to_log.__module__}.'
                         f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
                         )
            return res
        return decorated
