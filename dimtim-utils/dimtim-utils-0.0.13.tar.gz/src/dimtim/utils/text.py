import re
import unicodedata
from typing import Optional


def inline(value: str) -> str:
    return re.sub(r'\r?\n\s+', ' ', value).strip()


def slugify(value: str, allow_unicode: bool = False) -> str:
    if allow_unicode:
        value = unicodedata.normalize('NFKC', str(value))
    else:
        value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', value.lower()).strip())


def strip_markdown(value: str) -> str:
    try:
        from bs4 import BeautifulSoup
        import markdown
    except ImportError:
        raise ModuleNotFoundError(f'Mthod "{strip_markdown.__name__}" requred "beautifulsoup4" and "markdown" libraries')

    return BeautifulSoup(markdown.markdown(value), 'html.parser').text


def to_snake_case(text: str) -> str:
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)).lower()


def to_kebab_case(text: str) -> str:
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)).lower()


def to_camel_case(text: str) -> str:
    return ''.join(word.capitalize() for word in re.split(r'[ ._-]', text, re.MULTILINE))


KILOBYTE = 1024
MEGABYTE = 1048576
GIGABYTE = 1073741824
TERABYTE = 1099511627776
PETABYTE = 1125899906842624


def format_size(size: int) -> str:
    if size < KILOBYTE:
        return f'{size} b'
    if size < MEGABYTE:
        return f'{size / KILOBYTE:.2f} Kb'
    if size < GIGABYTE:
        return f'{size / MEGABYTE:.2f} Mb'
    if size < TERABYTE:
        return f'{size / GIGABYTE:.2f} Gb'
    if size < PETABYTE:
        return f'{size / TERABYTE:.2f} Tb'


def normalize_email(email: str) -> Optional[str]:
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except (ValueError, AttributeError):
        return None
    return '@'.join([email_name.lower(), domain_part.lower()])


def normalize_username(username: str) -> str:
    return unicodedata.normalize('NFKC', username) if username else username


def pluralize(value: int, one: str, two: str, five: str) -> str:
    ones = value % 10
    tens = value % 100
    return one if (ones == 1 and tens != 11) else two if (2 <= ones <= 4 and (tens < 10 or tens >= 20)) else five
