# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/11 11:04 AM
# LAST MODIFIED ON:
# AIM:
import re
from typing import List

from enum import Enum

regular_symbols = {
    '.': r'\.',
    '?': r'\?',
    '(': r'\(',
    ')': r'\)',
    '[': r'\[',
    ']': r'\]'
}


class Symbols(Enum):
    quotation_left = list('“')
    s_quota_left = list('‘')
    quotation_en = list('"')
    s_quota_en = list("'")
    quotation_right = list('”')
    s_quota_right = list('’')
    all_s_quota = list('‘’\'')
    all_quota = list('“"”')
    bracket_left = list('《<{[(（【「')
    bracket_right = list(')]}」】）>》')
    comma = list(',，')
    end_symbols = list('?!…？！。.')
    en_dot = list('.')
    dash = list('—')
    short_dash = list('-')
    all_dash = list('—-')
    semicolon = list(';；')
    colon = list('：:')

    @staticmethod
    def all_symbols():
        out = set()
        for v in Symbols:
            [out.add(vv) for vv in v.value]
        return ''.join(out)