import logging

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.logger.NehushtanLogging import NehushtanLogging

if __name__ == '__main__':
    file_logger = NehushtanFileLogger('test', '/Users/leqee/code/nehushtan/log', log_level=logging.INFO,
                                      print_higher_than_this_level=NehushtanLogging.INFO,
                                      record_millisecond=True)

    file_logger.critical('C', {"A": "B"})
    file_logger.error('E', 111)
    file_logger.warning('W', 'dd')
    file_logger.info('I', file_logger)
    file_logger.debug('D')

    try:
        raise ValueError('A<>B')
    except Exception as error:
        file_logger.exception('X', error)

    args_json = file_logger.get_args_json_to_clone()
    print(args_json)
    cloned_logger = NehushtanFileLogger.build_instance_from_args_json(args_json)

    cloned_logger.critical('C', {"A": "B"})
    cloned_logger.error('E', 111)
    cloned_logger.warning('W', 'dd')
    cloned_logger.info('I', cloned_logger)
    cloned_logger.debug('D')

    try:
        raise ValueError('A<>B')
    except Exception as error:
        cloned_logger.exception('X', error)

    progress_logger = NehushtanFileLogger()
    total = 36
    for i in range(total):
        progress_logger.log_progress('TEST', i, total, desc=f'now done[{i}]')
