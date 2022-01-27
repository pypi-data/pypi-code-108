# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import json
import logging
import sys
from datetime import datetime
from pkg_resources import resource_filename


class JSONFormatter(logging.Formatter):
    """Formats logging LogRecord() to JSON.
       Adds timestamp, and optionally, exc_info on exceptions.
    """
    def format(self, record):
        formatted_record = dict(
            event=record.getMessage(),
            time=datetime.utcnow().isoformat(),
            level=record.levelname
        )
        if record.exc_info:
            formatted_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(formatted_record)


def basic_json_logger(logger_name):
    """ Basic logging config which outputs WARNING level logs to stderr."""
    try:
        logger = logging.getLogger(logger_name)
        level = logging.WARNING
        logger.setLevel(level)
        logger.propagate = False
        for handler in logger.handlers:
            if handler.__class__ is logging.StreamHandler:
                break
        else:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            handler.setLevel(level)
            logger.addHandler(handler)
        return logger
    except:
        pass


# the controller parses this string, and uses the *last* 'x.x.x.x' version string to determine compatibility
def get_reported_version():
    return 'Python Agent v%s (proxy v%s) compatible with %s Python Version %s' % (get_agent_version(),
                                                                                  get_proxy_version(),
                                                                                  get_controller_dependency_version(),
                                                                                  get_python_version())


def get_agent_version_file():
    return resource_filename('appdynamics', 'VERSION')


def get_proxy_version_file():
    return resource_filename('appdynamics_bindeps.proxy', 'VERSION')


def get_controller_dependency_version_file():
    return resource_filename('appdynamics', 'CONTROLLER_DEPENDENCY_VERSION')


def get_agent_version(noisy=True):
    return get_version(get_agent_version_file(), noisy)


def get_proxy_version(noisy=True):
    return get_version(get_proxy_version_file(), noisy)


def get_controller_dependency_version(noisy=True):
    return get_version(get_controller_dependency_version_file(), noisy)


def get_version(version_file, noisy=True):
    try:
        with open(version_file, 'r') as f:
            version = f.read().split('.')
            # controller expects all agent versions to be of the form 1.2.3.4, so pad as necessary
            version.extend(['0'] * (4 - len(version)))
            return '.'.join(version)
    except:
        if noisy:
            logger = basic_json_logger('appdynamics.agent')
            logger.exception("Couldn't parse build info.")
        return 'unknown'


def get_python_version():
    return sys.version.split()[0]
