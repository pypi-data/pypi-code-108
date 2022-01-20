import datetime
import itertools
from collections import defaultdict

import pytz
from django.utils import timezone

from dateutil.parser import parse as _parse_dt
from django.utils.formats import sanitize_separators
from lxml import etree


def fast_iter(context, func):
    for event, elem in context:
        data = func(elem, event)
        if data is not None:
            yield data
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def elem2dict(node):
    """
    http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    :param node:
    :return:
    """
    node = node
    d = {node.tag: {} if node.attrib else None}
    children = list(node)
    if children:
        dd = defaultdict(list)
        for dc in map(elem2dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        # Todo:
        """
        <items buz="boo">
            <item bar=1>
            <item>
            <foo>
        </items>
        Must be converted to
        {
            'items': {
                '@buz': 'boo',
                '@children': [
                    {'item': {'@bar': 1}},
                    {'item': None},
                    {'foo': None}
                    ]
                }
        }
        """
        d = {node.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if node.attrib:
        d[node.tag].update(("@" + k, v) for k, v in node.attrib.items())
    if node.text:
        text = node.text.strip()
        if children or node.attrib:
            if text:
                d[node.tag]["#text"] = text
        else:
            d[node.tag] = text
    return d


class TIMEZONE:
    MSK = pytz.timezone("Europe/Moscow")
    UTC = timezone.utc


def parse_datetime(dt_string, tz=timezone.utc):
    """
    >>> parse_datetime("2018-12-12T07-55-29")
    datetime.datetime(2018, 12, 12, 7, 55, 29, tzinfo=<UTC>)
    >>> import pytz
    >>> parse_datetime("2018-12-12T07:55:29", tz=pytz.timezone("Europe/Moscow"))
    datetime.datetime(2018, 12, 12, 7, 55, 29, tzinfo=<DstTzInfo 'Europe/Moscow' MSK+3:00:00 STD>)
    >>> parse_datetime("2018-12-12T07:55:29+03:00", tz=pytz.timezone("Europe/Moscow"))
    datetime.datetime(2018, 12, 12, 7, 55, 29, tzinfo=<DstTzInfo 'Europe/Moscow' MSK+3:00:00 STD>)
    >>> parse_datetime("2018-12-12T00:25:12+00:00", tz=pytz.timezone("Europe/Moscow"))
    datetime.datetime(2018, 12, 12, 3, 25, 12, tzinfo=<DstTzInfo 'Europe/Moscow' MSK+3:00:00 STD>)

    :param dt_string:
    :param tz:
    :return:
    """
    dt = None
    try:
        dt = datetime.datetime.strptime(dt_string, "%Y-%m-%dT%H-%M-%S")
    except ValueError:
        dt = _parse_dt(dt_string)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, tz)
    else:
        dt = dt.astimezone(tz)
    return dt


def fix_dirty_decimal(value: str) -> str:
    """
    >>> fix_dirty_decimal('1345,12')
    '1345.12'
    >>> fix_dirty_decimal('1345,12')
    '1345.12'

    :param value:
    :return:
    """
    data = sanitize_separators(value)
    # Todo replace all i18n separators
    data = data.replace(",", ".").replace(" ", "")
    # dirty hack
    # if '.' not in data:
    #     # No dots
    #     return data
    #
    # *a, b = data.split('.')
    # if len(b) == 3:
    #     # FIXME
    #     # Пограничный случай, когда нет копеек
    #     # и это скорее всего разделитель тысяч
    #     # но предположение слишком смелое
    #     # 3,390 -> 3390
    #     a.append(b)
    #     return ''.join(a)
    # data = ''.join(a) + '.' + b
    return data


class XMLParser:
    def serialize(self, el, *args):
        dict_elem = elem2dict(el)
        return dict_elem

    def parse(self, xml_file, tags=None):
        context = etree.iterparse(xml_file, events=("end",), tag=tags)
        parsed = fast_iter(context, self.serialize)
        el = parsed.__next__()
        return itertools.chain([el], parsed)
