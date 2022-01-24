import os
import re
from collections import OrderedDict
from datetime import datetime
from logging import NullHandler, getLogger
from os.path import expanduser


INDENT = ' ' * 2
DATESTAMP_TEMPLATE = '%Y%m%d'
TIMESTAMP_TEMPLATE = DATESTAMP_TEMPLATE + '-%H%M'


def get_log(name):
    log = getLogger(name)
    log.addHandler(NullHandler())
    return log


def get_timestamp(when=None, template=TIMESTAMP_TEMPLATE):
    if when is None:
        # Use local time
        when = datetime.now()
    return when.strftime(template)


def format_summary(value_by_key, suffix_format_packs=None):
    suffix_format_packs = list(suffix_format_packs or [])
    suffix_format_packs.extend([
        ('_folder', format_path),
        ('_path', format_path),
    ])
    return format_nested_dictionary(OrderedDict(
        value_by_key), suffix_format_packs)


def format_path(x):
    return re.sub(r'^' + re.escape(expanduser('~')), '~', x)


def format_nested_dictionary(
        value_by_key, suffix_format_packs=None, prefix=''):
    parts = []
    for key, value in value_by_key.items():
        left_hand_side = prefix + str(key)
        if isinstance(value, dict):
            parts.append(format_nested_dictionary(
                value, suffix_format_packs, left_hand_side + '.'))
            continue
        for suffix, format_value in suffix_format_packs or []:
            if key.endswith(suffix):
                parts.append(format_assignment(
                    left_hand_side, format_value(value)))
                break
        else:
            value = str(value)
            if '\n' in value:
                value = format_indented_block(value)
            parts.append(format_assignment(
                left_hand_side, value))
    return '\n'.join(parts)


def format_assignment(left_hand_side, right_hand_side):
    left_hand_side = left_hand_side.strip()
    if right_hand_side.startswith('\n'):
        operator = ' ='
    else:
        operator = ' = '
        right_hand_side = right_hand_side.strip()
    return left_hand_side + operator + right_hand_side


def format_indented_block(x, indent=INDENT):
    return '\n' + '\n'.join(indent + line for line in x.splitlines())
