# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/10/12 5:40 PM
# LAST MODIFIED ON:
# AIM:

from typing import List
import abc

import re


class SequenceABC:
    def __init__(self, str_block: str):
        self.tokens = self.tokenizer(str_block)
        # -- pointers -- #
        self.__i = 0
        self.sentence_start = 0
        # --- bracket --- #
        self.bracket_left = 0
        self.bracket_right = 0
        # --- quota --- #
        self.quota_left = 0
        self.quota_right = 0
        self.quota_en = 0
        self.s_quota_en = 0
        self.s_quota_left = 0
        self.s_quota_right = 0

        # -- results -- #
        self.sentence_list_idx = []

        # -- init -- #
        if self.__i == 0:
            self.update_quota()
            self.update_bracket()

    def __str__(self):
        return self.current_token

    def __getitem__(self, item):
        if -len(self) <= item < len(self):
            return self.tokens[item]
        else:
            return ''

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        while self.current_token:
            yield self
            self.next()

    @property
    def current_token(self):
        return self[self.__i]

    @property
    def i(self) -> int:
        return self.__i

    @i.setter
    def i(self, value: int):
        # forward
        if value > self.__i:
            while self.__i != min(value, self.__len__()):
                self.next()
        # backward
        else:
            while self.__i != max(0, value):
                self.back()

    def get_result(self):
        out = []
        for v in self.sentence_list_idx:
            sentence = ''.join(self.tokens[v[0]:v[1]])
            if sentence:
                out.append(sentence)
        return out

    def get_right(self) -> str:
        i = self.__i + 1
        tok = self[i]
        return tok

    def get_left(self) -> str:
        i = self.__i - 1
        tok = self[i]
        return tok

    def get_left_interval(self, length: int = 1) -> str:
        string = ''
        i = self.__i
        for _ in range(length):
            i -= 1
            string = self[i] + string
        return string

    def get_right_interval(self, length: int = 1) -> str:
        string = ''
        i = self.__i
        for _ in range(length):
            i += 1
            string = string + self[i]
        return string

    def get_right_nearest_tok(self) -> str:
        i = self.__i + 1
        tok = self[i]
        length = len(self)
        while re.match(r'^\s+$', tok) and i < length:
            i += 1
            tok = self[i]
        return tok

    def get_left_nearest_tok(self) -> str:
        i = self.__i - 1
        tok = self[i]
        while re.match(r'^\s+$', tok) and i > 0:
            i -= 1
            tok = self[i]
        return tok

    def reset_bracket(self):
        self.bracket_right = 0
        self.bracket_left = 0

    def reset_quota(self):
        self.quota_right = 0
        self.quota_left = 0

    def reset_s_quota(self):
        self.s_quota_left = 0
        self.s_quota_right = 0

    # --- abstract layer -- #
    @abc.abstractmethod
    def tokenizer(self, str_block: str) -> List[str]:
        pass

    @abc.abstractmethod
    def update_quota(self):
        pass

    @abc.abstractmethod
    def degrade_quota(self):
        pass

    @abc.abstractmethod
    def update_bracket(self):
        pass

    @abc.abstractmethod
    def degrade_bracket(self):
        pass

    # -- basic action -- #
    def next(self):
        self.__i += 1
        self.update_bracket()
        self.update_quota()

    def back(self):
        self.degrade_bracket()
        self.degrade_quota()
        self.__i -= 1

    def add_to_results(self):
        self.sentence_list_idx.append((self.sentence_start, self.__i + 1))
        self.sentence_start = self.__i + 1
        self.next()
