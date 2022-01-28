import re
from datetime import datetime
from dateparser import parse

from .config import MYSQL_ENABLED, BLACKLIST_WORDS


def link_exist_in_db(href):
    if MYSQL_ENABLED:
        from .models import AnimeLink
        return AnimeLink.query.filter_by(link=href).first()
    return False


def parse_date(str_to_parse, date_format=''):
    if str_to_parse is None:
        date_to_format = datetime.fromtimestamp(0)
    elif isinstance(str_to_parse, datetime):
        date_to_format = str_to_parse
    else:
        date = parse(str_to_parse, date_formats=[date_format])
        if date:
            date_to_format = date
        else:
            date_to_format = datetime.fromtimestamp(0)

    return date_to_format.isoformat(' ', 'minutes')


def boldify(str_to_replace, keyword):
    if keyword:
        return re.sub('(%s)' % keyword, r'<b>\1</b>', str_to_replace, flags=re.IGNORECASE)
    else:
        return str_to_replace


def check_blacklist_words(url):
    return any(word.lower() in url.lower() for word in BLACKLIST_WORDS)


def check_if_vf(title):
    return any(word.lower() in title.lower() for word in ['vf', 'multi', 'french'])
