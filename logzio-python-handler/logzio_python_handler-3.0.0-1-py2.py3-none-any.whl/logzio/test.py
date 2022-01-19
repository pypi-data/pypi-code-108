import logging
import logging.config

# If you're using a serverless function, uncomment.
# from logzio.flusher import LogzioFlusher
import multiprocessing
import time
import logzio

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logzioFormat': {
            'format': '{"additional_field": "value"}',
            'validate': False
        }
    },
    'handlers': {
        'logzio': {
            'class': 'logzio.handler.LogzioHandler',
            'level': 'INFO',
            'formatter': 'logzioFormat',
            'token': 'zOqycKivEhCcuhVRdyMyDEjWBTqrNyGb',
            'logs_drain_timeout': 5,
            'url': 'https://listener.logz.io:8071',
            'retries_no': 4,
            'retry_timeout': 2,
            'debug': True
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['logzio'],
            'propagate': True
        }
    }
}
# Say I have saved my dictionary configuration in a variable named 'LOGGING' - see 'Dict Config' sample section
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('logzio')
logger2 = logging.getLogger('logzio2')
logger2.handlers = []
logger2.handlers = logger.handlers


# If you're using a serverless function, uncomment.
# @LogzioFlusher(logger)

def spawn_threads():
    logzio_handler = logzio.handler.LogzioHandler(
        token="zOqycKivEhCcuhVRdyMyDEjWBTqrNyGb",
        logzio_type='text',
        logs_drain_timeout=5,
        url='https://listener.logz.io:8071',
        debug=True,
        backup_logs=True,
        network_timeout=10.0
    )
    thread_list = []
    logger_2 = logging.getLogger("logzio")
    logger_2.info("Starting logging from main")
    print("Starting logging from main")
    for i in range(1, 7):
        if i % 2 == 0:
            logger_2 = logging.getLogger('logzio')
        else:
            logger_2 = logging.getLogger('logzio2')
        thread = multiprocessing.Process(target=thread_check, args=(logger_2,))
        thread_list.append(thread)
        thread.start()

    time.sleep(5)
    for thread in thread_list:
        thread.join()


def thread_check(logger):
    time.sleep(5)
    # logger=logging.getLogger('logzio')
    print("thread " + multiprocessing.current_process().name + " started, logger: {logger}")
    for i in range(1, 4):
        logger.info("Logging thread: " + multiprocessing.current_process().name + " try " + str(i) + "/3")
        print("Logged thread " + multiprocessing.current_process().name)
        time.sleep(2)


def my_func():
    logger.info('Test log')
    logger.warning('Warning')

    try:
        1 / 0
    except:
        logger.exception("Supporting exceptions too!")


if __name__ == '__main__':
    spawn_threads()
