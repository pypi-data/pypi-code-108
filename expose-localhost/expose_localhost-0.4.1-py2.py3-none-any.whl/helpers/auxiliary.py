import json
import sys
from datetime import datetime
from inspect import currentframe, getframeinfo, getouterframes, stack
from time import sleep
from urllib.request import urlopen

DATETIME_FORMAT = '%b-%d-%Y %I:%M:%S %p'
IP_INFO = json.load(urlopen('http://ipinfo.io/json')) or json.load(urlopen('http://ip.jsontest.com'))


def sleeper(sleep_time: int) -> None:
    """Sleeps for a particular duration and prints the remaining time in console output.

    Args:
        sleep_time: Takes the time script has to sleep, as an argument.
    """
    sleep(1)
    for i in range(sleep_time):
        sys.stdout.write(f'\rRemaining: {sleep_time - i:0{len(str(sleep_time))}}s')
        sleep(1)
    sys.stdout.flush()
    sys.stdout.write('\r')


def time_converter(seconds: float) -> str:
    """Modifies seconds to appropriate days/hours/minutes/seconds.

    Args:
        seconds: Takes number of seconds as argument.

    Returns:
        str:
        Seconds converted to days or hours or minutes or seconds.
    """
    days = round(seconds // 86400)
    seconds = round(seconds % (24 * 3600))
    hours = round(seconds // 3600)
    seconds %= 3600
    minutes = round(seconds // 60)
    seconds %= 60
    if days:
        return f'{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds'
    elif hours:
        return f'{hours} hours, {minutes} minutes, and {seconds} seconds'
    elif minutes:
        return f'{minutes} minutes, and {seconds} seconds'
    elif seconds:
        return f'{seconds} seconds'


def prefix(level: str = 'DEBUG') -> str:
    """Replicates the logging config to print colored statements accordingly.

    Args:
        level: Takes the log level as an argument.

    Returns:
        str:
        A well formatted prefix to be added before a print statement.
    """
    calling_file = getouterframes(currentframe(), 2)[1][1].split('/')[-1].rstrip('.py')
    return f"{datetime.now().strftime(DATETIME_FORMAT)} - {level} - [{calling_file}:" \
           f"{getframeinfo(stack()[1][0]).lineno}] - {stack()[1].function} - "
