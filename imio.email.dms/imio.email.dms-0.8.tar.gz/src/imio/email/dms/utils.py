# -*- coding: utf-8 -*-
from email import generator


def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except:
            value = value.decode('utf-8', 'replace')
    return value


def save_as_eml(path, message):
    with open(path, 'w') as emlfile:
        gen = generator.Generator(emlfile)
        gen.flatten(message)
