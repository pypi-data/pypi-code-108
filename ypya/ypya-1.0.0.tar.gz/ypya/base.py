'''
ypya.base
'''
import logging


class YBase(object):
    '''
    basic declaration
    '''

    INCLUDE_DEBUG_FIELD = True
    INCLUDE_EXTRA_FIELD = True


class GELFData(object):
    '''
    data type adapter for GELF
    '''
    SYSLOG_LEVELS = {
        logging.CRITICAL: 2,
        logging.ERROR: 3,
        logging.WARNING: 4,
        logging.INFO: 6,
        logging.DEBUG: 7,
    }

    SPECIAL_NAME_PREFIX = '_'
    GELF_VERSION_NUMBER = '1.0'

    BASIC_FIELDS = (
        'version',
        'timestamp',
        'host',
        'facility',
        'level',
        'short_message',
        'full_message',
    )
