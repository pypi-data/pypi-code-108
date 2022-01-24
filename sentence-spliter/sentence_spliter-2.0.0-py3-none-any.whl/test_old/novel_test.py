# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/1/27 3:20 PM
# LAST MODIFIED ON:
# AIM:
import os
from typing import List

from sentence_spliter_old.automata.symbols import SYMBOLS_EN


def tokenize(sentence: str):
    return SYMBOLS_EN['all_symbols'].split(sentence)


def check_comma(sentence_list: List[str]):
    for sentence in sentence_list:
        count = 0
        for v in tokenize(sentence):
            if SYMBOLS_EN['all_quota'].match(v):
                count += 1


def test_whole_novel(novel_dir: str):
    for file in os.listdir(novel_dir):
        name, extends = os.path.splitext(file)
        if extends == '.txt':
            file_path = os.path.join(novel_dir, file)
            pass
