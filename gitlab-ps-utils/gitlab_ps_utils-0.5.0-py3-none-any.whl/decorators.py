from traceback import print_exc
from os import getenv
from time import sleep
from functools import wraps
from gitlab_ps_utils.logger import myLogger
from gitlab_ps_utils.exceptions import ConfigurationException

log = myLogger(__name__, app_path=getenv('APP_PATH', '.'),
               log_name=getenv('APP_NAME', 'application'))


def stable_retry(function, ExceptionType=Exception, delay=5, backoff=1.20):
    @wraps(function)
    def f_retry(*args, **kwargs):
        retries = 3
        mretries, mdelay = retries, delay
        while mretries >= 0:
            try:
                return function(*args, **kwargs)
            except ConfigurationException:
                return function(*args, **kwargs)
            except ExceptionType as e:
                log.error(
                    "{0}, Api connecion failed Retrying in {1} seconds...".format(e, mdelay))
                log.error(print_exc())
                sleep(mdelay)
                mretries -= 1
                mdelay *= backoff
        log.error("Failed to connect to API within {0} retr{1}".format(
            retries, "y" if retries else "ies"))
    return f_retry


def configurable_stable_retry(ExceptionType=Exception, retries=3, delay=5, backoff=1.20):
    def stable_retry(function, ExceptionType=ExceptionType,
                     retries=retries, delay=delay, backoff=backoff):
        def f_retry(*args, **kwargs):
            mretries, mdelay = retries, delay
            while mretries >= 0:
                try:
                    return function(*args, **kwargs)
                except ExceptionType as e:
                    log.error(
                        "{0}, Api connecion failed Retrying in {1} seconds...".format(e, mdelay))
                    sleep(mdelay)
                    mretries -= 1
                    mdelay *= backoff
            log.error("Failed to connect to API within {0} retr{1}".format(
                retries, "y" if retries else "ies"))
            log.error(print_exc())
        return f_retry
    return stable_retry


def token_rotate(function):
    """
        Decorator used to rotate token used from a list

        This decorator assumes args[0] is `self` in a class
        and the class needs to have a `token_array` instance
        attribtue and `index` class attribute
    """
    @wraps(function)
    def f_rotate(*args, **kwargs):
        tokens = args[0].token_array
        if tokens and len(tokens) > 1:
            args[0].index += 1
            index = args[0].index % len(tokens)
            log.debug(f"Rotating to token index {index}")
            args[0].token = tokens[index]
        elif not tokens:
            log.info("No tokens provided")
        return function(*args, **kwargs)
    return f_rotate
