# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/11 11:02 AM
# LAST MODIFIED ON:
# AIM:
import re
from typing import List

from sentence_spliter.architect.sequence import SequenceABC
from sentence_spliter.en_cutter.symbol import Symbols
from sentence_spliter.utility.arrary import flatten


class Sequence(SequenceABC):
    def __init__(self, str_block: str):
        super(Sequence, self).__init__(str_block)
        self.n_words = 0
        self.word_pattern = re.compile(r'[a-zA-Z0-9]+')

    def next(self):
        if self.word_pattern.match(self.current_token):
            self.n_words += 1
        super(Sequence, self).next()

    def back(self):
        if self.word_pattern.match( self.current_token):
            self.n_words = max(0, self.n_words - 1)
        super(Sequence, self).back()
        
    def add_to_results(self):
        self.n_words = 0
        super(Sequence, self).add_to_results()

    def tokenizer(self, str_block: str) -> List[str]:
        pattern = '(' + "|".join(Symbols.all_dash.value) + ')'
        dash_pattern = re.compile(pattern)
        str_list = flatten([dash_pattern.split(v) for v in re.split(r'(\s+)', str_block) if v])
        out = []
        # -- #
        for tok in str_list:
            tok_list = list(tok)
            while tok_list and tok_list[0] in Symbols.all_symbols():
                out.append(tok_list[0])
                tok_list.pop(0)
            temp = []
            while tok_list and tok_list[-1] in Symbols.all_symbols():
                temp.append(tok_list[-1])
                tok_list.pop()
            if tok_list:
                out.append(''.join(tok_list))
            if temp:
                out.extend(temp[::-1])
        return out

    def update_quota(self):

        if self.current_token in Symbols.s_quota_en.value:
            self.s_quota_en = (self.s_quota_en + 1) % 2
        if self.current_token in Symbols.s_quota_left.value:
            self.s_quota_left += 1
        if self.current_token in Symbols.s_quota_right.value:
            self.s_quota_right += -1
        if self.current_token in Symbols.quotation_en.value:
            self.quota_en = (self.quota_en + 1) % 2
        if self.current_token in Symbols.quotation_left.value:
            self.quota_left += 1
        if self.current_token in Symbols.quotation_right.value:
            self.quota_right += -1

    def degrade_quota(self):
        if self.current_token in Symbols.all_quota.value or \
                self.current_token in Symbols.all_s_quota.value:
            if self.current_token in Symbols.s_quota_en.value:
                self.s_quota_en = (self.s_quota_en - 1) % 2
            if self.current_token in Symbols.s_quota_left.value:
                self.s_quota_left -= 1
            if self.current_token in Symbols.s_quota_right.value:
                self.s_quota_right += 1
            if self.current_token in Symbols.quotation_en.value:
                self.quota_en = (self.quota_en - 1) % 2
            if self.current_token in Symbols.quotation_left.value:
                self.quota_left -= 1
            if self.current_token in Symbols.quotation_right.value:
                self.quota_right += 1

    def update_bracket(self):
        if self.current_token in Symbols.bracket_right.value:
            self.bracket_right -= 1
        if self.current_token in Symbols.bracket_left.value:
            self.bracket_left += 1

    def degrade_bracket(self):
        if self.current_token in Symbols.bracket_right.value:
            self.bracket_right += 1
        if self.current_token in Symbols.bracket_left.value:
            self.bracket_left -= 1