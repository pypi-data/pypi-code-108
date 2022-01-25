import logging
import os

import click

import puddl

LOG_LEVELS = ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG']


@click.group()
@click.option(
    '-l', '--log-level', type=click.Choice(LOG_LEVELS, case_sensitive=False), default=os.environ.get('LOGLEVEL')
)
@click.option('-d', '--debug', is_flag=True, help='sets log level to DEBUG. ignores "--log-level"')
@click.option('--loggers', default='', help='comma-separated logger names')
@click.version_option(version=puddl.__version__)
def root(log_level, debug, loggers):
    if debug:
        log_level = 'DEBUG'
    # longest level is WARNING with 7 character
    logging.basicConfig(level=log_level, format='%(name)s %(levelname)-7s %(msg)s')
    if loggers:
        for name in loggers.split(','):
            logging.getLogger(name).setLevel(log_level)
    pass
