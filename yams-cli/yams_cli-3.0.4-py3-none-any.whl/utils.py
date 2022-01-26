#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json
import logging
import keyword
import string
import random
import pkg_resources
from dateutil.parser import parse
from pytz import utc

log = logging.getLogger('yams-client')


def configure_logging(loglevel, logfile=None):
    """ Configure logging to the defined level using (if provided) a file.
    :param loglevel: logging level
    :param logfile: file to write the logs
    :return:
    """
    loglevel = loglevel.upper()
    loglevels = ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    if loglevel not in loglevels:
        raise Exception('"loglevel" must be one of {}'.format(loglevels))

    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%m-%d %H:%M:%S',
        level=loglevel,
        stream=sys.stderr)


def retrieve_action(options, allowed_commands):
    """ Given the cli input options, return the one to be executed.
    :param options:
    :param allowed_commands:
    :return:
    """
    actions = filter(lambda opt: not opt.startswith('<') and not opt.startswith('-') and opt in allowed_commands,
                     options.keys())

    for action in actions:
        if options[action]:
            action = action.replace('-', '_')
            if keyword.iskeyword(action):
                action = '{}_'.format(action)
            return action


def is_action_confirmed(element_id, command, action):
    msg = 'Trying to {} the {} id {}. Should we proceed?'.format(action, command, element_id)
    return input("%s (y/N) " % msg).lower() == 'y'


def exception_safe(exception):
    """
    Catch the exception, log it and return a value
    """

    def decorator(func):
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except exception as e:
                log.error("A '{}' occurred: {}".format(type(e).__name__, e))

        return wrapper

    return decorator


def dispatcher_exception_safe(exception):
    """
    Catch the exception, log it and return a value
    """

    def decorator(func):
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except exception as e:
                log.error("A '{}' occurred".format(type(e).__name__))
                if hasattr(e, "message"):
                    print(e.message)
                else:
                    print(e)
                return False

        return wrapper

    return decorator


def generate_pretty_print(content):
    """ Pretty printing the json content.
    :param content:
    :return:
    """
    return json.dumps(content, sort_keys=True, indent=4, separators=(',', ': '))


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generates a random string.
    :param size: integer. Resulting random string length
    :param chars: characters list. Input characters to generate the random string
    :return:
    """
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def get_directory(filename):
    directories = filename.split("/")
    directory = ""
    for i in range(len(directories) - 1):
        directory += directories[i] + "/"
    return directory


def valid_uuid(uuid):
    regex = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def get_version():
    try:
        version = pkg_resources.require("yams-cli")[0].version
    except pkg_resources.ResolutionError:
        version = '0.0.1'

    return version


def is_date(text, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param text: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        date = parse(text, fuzzy=fuzzy)
        return date.replace(tzinfo=utc), True
    except Exception:
        return None, False


def get_timestamp(text):
    (date, is_valid_date) = is_date(text)
    if not is_valid_date:
        return int(text)
    else:
        return int(date.timestamp())


def is_not_blank(my_string):
    return bool(my_string and my_string.strip())
