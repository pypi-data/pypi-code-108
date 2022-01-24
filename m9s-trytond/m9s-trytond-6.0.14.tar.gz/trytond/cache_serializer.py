# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import datetime
import msgpack

from decimal import Decimal
from lxml import etree

__all__ = ['pack', 'unpack']


def encode_hook(o):
    from trytond.model import Model
    if isinstance(o, Decimal):
        return {
            '__decimal__': True,
            'data': str(o)
        }
    if isinstance(o, datetime.datetime):
        return {
            '__datetime__': True,
            'data': (o.year, o.month, o.day, o.hour, o.minute, o.second,
                o.microsecond)
        }
    if isinstance(o, datetime.date):
        return {
            '__date__': True,
            'data': (o.year, o.month, o.day)
        }
    if isinstance(o, datetime.time):
        return {
            '__time__': True,
            'data': (o.hour, o.minute, o.second, o.microsecond)
        }
    if isinstance(o, datetime.timedelta):
        return {
            '__timedelta__': True,
            'data': o.total_seconds()
        }
    if isinstance(o, set):
        return {
            '__set__': True,
            'data': tuple(o)
        }
    if isinstance(o, etree._Element):
        return {
            '__etree_Element__': True,
            'data': etree.tostring(o)
        }
    if isinstance(o, Model):
        return {
            '__tryton_model__': True,
            'data': str(o)
        }
    return o


def decode_hook(o):
    if '__decimal__' in o:
        return Decimal(o['data'])
    elif '__datetime__' in o:
        return datetime.datetime(*o['data'])
    elif '__date__' in o:
        return datetime.date(*o['data'])
    elif '__time__' in o:
        return datetime.time(*o['data'])
    elif '__timedelta__' in o:
        return datetime.timedelta(o['data'])
    elif '__set__' in o:
        return set(o['data'])
    elif '__etree_Element__' in o:
        return etree.fromstring(o['data'])
    elif '__tryton_model__' in o:
        model, id = o['data'].split(',')
        from trytond.pool import Pool
        return Pool().get(model)(int(id))
    return o


def pack(value):
    return msgpack.packb(value, use_bin_type=True, default=encode_hook)


def unpack(bundle):
    return msgpack.unpackb(bundle, raw=False, object_hook=decode_hook)
