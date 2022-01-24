# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/12 4:42 PM
# LAST MODIFIED ON:
# AIM:
import re

SYMBOLS = {
    'quotation_left': re.compile(r'([“])'),
    'quotation_en': re.compile(r'(["])'),
    'quotation_right': re.compile(r'([”])'),
    'bracket_left': re.compile(r'([<{\[\(（【「])'),
    'bracket_right': re.compile(r'([\)\]}」】）>])'),
    'book_left': re.compile(r'([《])'),
    'book_right': re.compile(r'([》])'),
    'comma': re.compile(r'([,，;])'),
    'end_symbols': re.compile(r'([?\!…;？！。\.])'),
    'en_dot': re.compile(r'\.'),
    'all_symbols': re.compile(r'([\]\(【\?】。,！[”，\!\.「<>？"（“…《）}》」;:：\){\)\s])')
}


SYMBOLS_EN = {
    'quotation_left': re.compile(r'([“])'),
    's_quota_left': re.compile(r'([‘])'),
    'quotation_en': re.compile(r'(["])'),
    's_quota_en':  re.compile("(['])"),
    'quotation_right': re.compile(r'([”])'),
    's_quota_right': re.compile(r'([’])'),
    'all_s_quota': re.compile(r'([‘’\'])'),
    'all_quota': re.compile(r'([“"”])'),
    'bracket_left': re.compile(r'([<{\[\(（【「])'),
    'bracket_right': re.compile(r'([\)\]}」】）>])'),
    'book_left': re.compile(r'([《])'),
    'book_right': re.compile(r'([》])'),
    'comma': re.compile(r'([,，])'),
    'end_symbols': re.compile(r'([?\!…？！。\.])'),
    'en_dot': re.compile(r'\.'),
    'dash': re.compile(r'—'),
    'short_dash': re.compile(r'-'),
    'semicolon': re.compile(r'([;；])'),
    'all_symbols': re.compile(r'([\]\(【\?】。,！[”，\!\.「<>？"（“…《）}》」;；:：\'‘’\-\—\){\)\s])')
}
