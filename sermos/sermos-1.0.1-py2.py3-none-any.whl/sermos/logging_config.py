import os
import logging
import logging.config
from sermos import __version__
from logging import StreamHandler

logging_set = False


def get_log_level(level: str = None) -> int:
    """ Attempt to get the log level from the environment, otherwise use the
        default INFO level.  The environment variable LOG_LEVEL should be e.g.,
        'DEBUG'
    """
    if level is not None:
        level_str = str(level)
    else:
        level_str = os.environ.get('LOG_LEVEL', 'INFO')
    return getattr(logging, level_str)


def get_log_format(type: str = 'standard',
                   app_version: str = None,
                   client_version: str = None):
    """ Standard log format. Supports `standard` and `simple`
    """
    if app_version is None:
        app_version = "?"
    if client_version is None:
        client_version = "?"

    format = '%(message)s'
    if type == 'standard':
        format = '%(process)d - %(levelname)s - %(asctime)s - '\
            + '%(filename)s (%(lineno)d) - '\
            + 'sermos v{} - client v{} - %(message)s'\
            .format(app_version, client_version)
    elif type == 'simple':
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    elif type == 'proxy':
        format = 'Sermos v{} Cloud Proxy [%(levelname)s] > %(message)s'.format(
            app_version)

    return format


def get_date_format():
    """ Standard date format
    """
    return '%Y-%m-%dT%H:%M:%S'


def setup_logging(app_version: str = None,
                  client_version: str = None,
                  default_level: str = None,
                  overload_elasticsearch: bool = False,
                  establish_logging_config: bool = True):
    """ Setup logging configuration for standard streaming output + optional
        log aggregator.

        Standard usage is to invoke this at application bootstrapping time
        to establish default log handling. e.g.

        def create_app():
            setup_logging()

        Individual application modules should load a logger like normal:
        import logging
        logger = logging.getLogger(__name__)

        elasticsearch-py is overly verbose with it's 'info' logging. This
        will set that logger to `warning` if `overload_elasticsearch` is True

        `establish_logging_config` is intended to be used by something invoking
        setup_logging() explicitly with the intention of setting the final
        configuration, which is the default behavior. Set this to `False` in the
        case where you might not be sure if logging has been set up yet.
    """
    global logging_set

    if logging_set and not establish_logging_config:
        return

    if establish_logging_config or not logging_set:
        logging_set = True

    # Set our application version values, which can be passed to this method.
    # By default, we report the app versions for sermos and the client
    A_VERSION = __version__  # sermos version
    CA_VERSION = None  # application version of client app using sermos
    if app_version is not None:
        A_VERSION = app_version
    if client_version is not None:
        CA_VERSION = client_version

    log_level = get_log_level(default_level)

    config = {
        'disable_existing_loggers': False,
        'version': 1,
        'formatters': {
            'simple': {
                'format':
                get_log_format(type='simple',
                               app_version=A_VERSION,
                               client_version=CA_VERSION),
                'datefmt':
                get_date_format()
            },
            'standard': {
                'format':
                get_log_format(type='standard',
                               app_version=A_VERSION,
                               client_version=CA_VERSION),
                'datefmt':
                get_date_format()
            },
            'proxy': {
                'format': get_log_format(type='proxy', app_version=A_VERSION),
                'datefmt': get_date_format()
            },
        },
        'handlers': {
            'consoleFull': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            },
            'proxyHandler': {
                'level': 'DEBUG',
                'formatter': 'proxy',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {
                'handlers': ['consoleFull'],
                'level': 'ERROR',
            },
            'sermos': {
                'handlers': ['consoleFull'],
                'level': 'DEBUG',
                'propagate': False
            },
            'timing': {
                'handlers': ['consoleFull'],
                'level': 'DEBUG',
                'propagate': False
            },
            'celery': {
                'handlers': ['consoleFull'],
                'level': 'DEBUG',
                'propagate': False
            },
            'bin': {
                'handlers': ['consoleFull'],
                'level': 'DEBUG',
                'propagate': False
            },
            'sermos.proxy': {
                'handlers': ['proxyHandler'],
                'level': 'DEBUG',
                'propagate': False
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['consoleFull']
        }
    }

    for handler, handler_config in config['handlers'].items():
        # Override this handler's level to the level passed to this method
        handler_config['level'] = log_level
        config['handlers'][handler] = handler_config

    # Set the root handler's level
    config['root']['level'] = log_level

    logging.config.dictConfig(config)

    es_logger = logging.getLogger('elasticsearch')
    if overload_elasticsearch is True:
        es_logger.setLevel(logging.WARNING)
    else:
        # Ensure to set to baseline in the event this is invoked multiple times.
        es_logger.setLevel(logging.INFO)
