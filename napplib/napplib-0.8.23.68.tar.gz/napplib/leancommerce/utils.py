import functools
import logging
from datetime import datetime, timedelta
from time import sleep

requests_remaining_config = {'total_remaining': 200, 'count': 0, 'time': 60, 'execute_time': None}

# set logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")


def requests_remaining(func):
    """[
    decorator should not exceed 200 requests per minute, if 200 requests occur in less than a minute,
    the next request within 1 minute will wait for the remaining time before running again. 

    # -------------- decorator config -------------- #
    requests_remaining_config = {'total_remaining': 200, 'count': 0, 'time': 1, 'execute_time': None}

    # -------------- decorator config values -------------- #
    total_remaining = is the total number of requests
    count = is a counter to verify and validate with total_remaining, always leave at 0
    time = time without seconds that defines the total number of requests
    exexcute_time = is a datetime with the current time of execution to start the validation
    ]

    Args:
        func ([obj]): [Function object]

    Returns:
        [dict]: [func_return and time_left to renew requests]
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = requests_remaining_config
        if config['execute_time'] == None or not isinstance(config['execute_time'], datetime):
            config['execute_time'] = datetime.now()

        now_time = datetime.now()
        time_to_renew = timedelta(seconds=config['time'])
        total_time = now_time - config['execute_time']
        time_left = time_to_renew - total_time
        value = None

        if total_time >= time_to_renew:
            logging.info(f'Renewing requests! - Resquest time {now_time - config["execute_time"]}')
            config['execute_time'] = datetime.now()
            config['count'] = 0

            value = func(*args, **kwargs)
            config['count'] += 1
        else:
            if config['count'] < config['total_remaining']:
                value = func(*args, **kwargs)

                config['count'] += 1
                logging.info(f"Requests remaining {config['total_remaining'] - config['count']}")
            else:
                logging.warning(f"requests are over, wait for {time_left} for {config['total_remaining']} more requests")
                sleep(round(time_left.total_seconds())+1)
                wrapper(*args, **kwargs)
        return value
    return wrapper
