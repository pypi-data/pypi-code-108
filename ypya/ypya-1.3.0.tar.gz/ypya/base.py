'''
ypya.base
'''
import json
import logging
import traceback


class YBase(object):
    '''
    basic declaration
    '''

    INCLUDE_DEBUG_FIELD = True
    INCLUDE_EXTRA_FIELD = True
    INCLUDE_FULLY_QUALIFIED_NAME = False
    INCLUDE_LEVEL_SYMBOLIC_NAME = False

    def makePickle(self, record):
        '''
        public method

        :param record: (logging.LogRecord)
        :return: (stringified JSON)
        '''
        obj = GELFData(record)
        setattr(obj, 'parent', self)
        return obj.data


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

    def __init__(self, record):
        '''
        :param record: (logging.LogRecord)
        '''
        assert record is not None, 'invalid argument value'
        self.instance = record

    @property
    def data(self):
        '''
        :return: (string/unicode)
        '''
        self.cache = dict()

        self.collect_basic_fields()

        # rval;
        rval = json.dumps(self.cache)
        return rval

    def collect_basic_fields(self):
        '''
        :return: (dict)
        '''
        self.cache['version'] = self.GELF_VERSION_NUMBER
        self.cache['timestamp'] = self.instance.created
        self.cache['level'] = self.SYSLOG_LEVELS.get(
            self.instance.levelno,
            self.instance.levelno
        )
        self.cache['host'] = self.parent.sender_host
        self.cache['facility'] = self.parent.sender_name or self.instance.name

        formatter = getattr(self, 'formatter', None)
        self.cache['short_message'] = formatter.format(self.instance) if formatter else self.instance.getMessage(),
        self.cache['full_message'] = formatter.format(self.instance) if formatter else self.extract_full_message(self.instance)

        return self.cache

    def extract_full_message(self, record):
        '''
        :param record: (logging.LogRecord)
        '''
        if record.exc_info:
            items = traceback.format_exception(*record.exc_info)
            msg = '\n'.join(items)
        elif record.exc_text:
            msg = record.exc_text
        else:
            msg = record.getMessage()
        return msg
