# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/15 3:21 PM
# LAST MODIFIED ON:
# AIM:
from typing import List, Union
import re
import pathlib
import os

from sentence_spliter.architect.graph_component import Condition
from sentence_spliter.zh_cutter.symbol import Symbols
from sentence_spliter.zh_cutter.zh_sequence import Sequence
from sentence_spliter.utility.file_opt import read_file
from sentence_spliter.utility.trie import Trie

PATH = str(pathlib.Path(__file__).absolute().parent)
WHITE_LIST_PATH = os.path.join(PATH, 'white_list.txt')


class IsEndState(Condition):
    def __init__(self) -> object:
        super(IsEndState, self).__init__('IsEndState')

    def run(self, tok: Sequence):
        return tok.current_token == ''


class IsEndSymbol(Condition):
    def __init__(self, name: str = 'IsEndSymbol', reverse: bool = False):
        super(IsEndSymbol, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        return tok.current_token in Symbols.end_symbols.value


class IsBracketClose(Condition):
    def __init__(self, name: str = 'IsBracketClose', reverse: bool = False):
        super(IsBracketClose, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        if tok.bracket_left + tok.bracket_right == 0:
            tok.reset_bracket()
            return True
        return False


class IsQuotaClose(Condition):
    def __init__(self, name: str = 'IsQuotaClose', reverse: bool = False):
        super(IsQuotaClose, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        if tok.current_token in Symbols.quotation_right.value:
            return True
        if abs(tok.quota_right + tok.quota_left) + tok.quota_en == 0:
            return True
        return False


class IsSingleQuotaClose(Condition):
    def __init__(self, name: str = 'IsSingleQuotaClose', reverse: bool = False):
        super(IsSingleQuotaClose, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        if abs(tok.s_quota_left + tok.s_quota_right) + tok.s_quota_en == 0:
            tok.reset_s_quota()
            return True
        return False


class IsBlank(Condition):
    def __init__(self, name: str = 'IsBlank', reverse: bool = False):
        super(IsBlank, self).__init__(name, reverse)
        self.pattern = re.compile(r'^\s+$')

    def run(self, tok: Sequence) -> bool:
        if self.pattern.match(tok.current_token):
            return True
        else:
            return False


class TokenInWhiteList(Condition):
    def __init__(self, name: str = 'TokenInWhiteList', reverse: bool = False):
        super(TokenInWhiteList, self).__init__(name, reverse)
        self.white_list = Trie('<root>')
        for value in read_file(WHITE_LIST_PATH).splitlines():
            if not re.match('[a-zA-Z]', value[-1]):
                token_list = value[0:-1].split() + [value[-1]]
            else:
                token_list = value.split()
            self.white_list.add_phrase(token_list[::-1])

    def run(self, tok: Sequence) -> bool:
        verb = tok.current_token
        i = tok.i - 1
        tree = self.white_list
        while verb in tree:
            if re.match(r'^\s+$', verb):
                continue
            tree = tree[verb]
            verb = tok[i]
            i -= 1

        if tree.is_end_node(tok[i]):
            return True
        return False


class IsRightQuota(Condition):
    def __init__(self, name: str = 'IsRightQuota', reverse: bool = False):
        super(IsRightQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.current_token
        if tok in Symbols.quotation_right.value:
            return True
        if seq.quota_en == 0 and seq.current_token in Symbols.quotation_en.value:
            return True
        return False


class IsLeftQuota(Condition):
    def __init__(self, name: str = 'IsLeftQuota', reverse: bool = False):
        super(IsLeftQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.current_token
        if tok in Symbols.quotation_left.value:
            return True
        if seq.quota_en == 1 and seq.current_token in Symbols.quotation_en.value:
            return True
        return False


class IsRightBeforeLeftQuota(Condition):
    def __init__(self, name: str = 'IsRightBeforeLeftQuota', reverse: bool = False):
        super(IsRightBeforeLeftQuota, self).__init__(name, reverse)
        self.right_quota = IsRightQuota()

    def run(self, seq: Sequence):
        next_tok = seq.get_right_nearest_tok()
        if self.right_quota(seq) and (
                next_tok in Symbols.quotation_left.value or next_tok in Symbols.quotation_en.value):
            return True
        return False


class IsRightSingleQuota(Condition):
    def __init__(self, name: str = "IsRightSingleQuota", reverse: bool = False):
        super(IsRightSingleQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.current_token
        if tok in Symbols.s_quota_right.value:
            return True
        if seq.quota_en == 0 and seq.current_token in Symbols.s_quota_en.value:
            return True
        return False


class IsLeftSingleQuota(Condition):
    def __init__(self, name: str = "IsLeftSingleQuota", reverse: bool = False):
        super(IsLeftSingleQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.current_token
        if tok in Symbols.s_quota_left.value:
            return True
        if seq.quota_en == 1 and seq.current_token in Symbols.s_quota_en.value:
            return True
        return False


class IsNumberDot(Condition):
    """
    case 1. go to bed.
    or   1.1. go to bed.

    1. may not be a sentence 
    """

    def __init__(self, name: str = 'IsNumberDot', reverse: bool = False):
        super(IsNumberDot, self).__init__(name, reverse)
        self.pattern = re.compile(r'^\d+(.\d+)*$')

    def run(self, tok: Sequence) -> bool:
        if tok.current_token == '.' and self.pattern.match(tok[tok.i - 1]):
            return True
        return False


class NextStartWithCapital(Condition):
    def __init__(self, name: str = 'NextStartWithCapital', reverse: bool = False):
        super(NextStartWithCapital, self).__init__(name, reverse)
        self.pattern = re.compile(r'^[A-Z]+[a-z]*')

    def run(self, tok: Sequence) -> bool:
        return bool(self.pattern.match(tok[tok.i + 2]))


class NextStartWithNum(Condition):
    def __init__(self, name: str = 'NextStartWithNum', reverse: bool = False):
        super(NextStartWithNum, self).__init__(name, reverse)
        self.pattern = re.compile(r'^\d')

    def run(self, tok: Sequence) -> bool:
        return bool(self.pattern.match(tok[tok.i + 2]))


class IsSentenceDash(Condition):
    def __init__(self, name: str = 'IsSentenceDash', reverse: bool = False):
        super(IsSentenceDash, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        if tok.current_token in Symbols.dash.value:
            return True
        if tok.current_token in Symbols.short_dash.value and tok[tok.i - 1] in Symbols.short_dash.value:
            return True
        return False


class IsComma(Condition):
    def __init__(self, name: str = 'IsComma', reverse: bool = False):
        super(IsComma, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        if tok.current_token in Symbols.comma.value:
            return True
        return False


# --- long short handler -- #
class IsLongSentence(Condition):
    def __init__(self, max_length: int = 40, name: str = 'IsLongSentence', reverse: bool = False):
        super(IsLongSentence, self).__init__(name, reverse)
        self.max_length = max_length

    def run(self, tok: Sequence) -> bool:
        return tok.n_words >= self.max_length - 1


class IsShortSentence(Condition):
    def __init__(self, min_length: int = 6, name: str = 'IsShortSentence', reverse: bool = False):
        super(IsShortSentence, self).__init__(name, reverse)
        self.min_length = min_length

    def run(self, tok: Sequence) -> bool:
        return tok.n_words < self.min_length


class RightQuotaAfterEnd(Condition):
    def __init__(self, name='RightQuotaAfterEnd', reverse: bool = False):
        super(RightQuotaAfterEnd, self).__init__(name, reverse)
        self.is_right_quota = IsRightQuota().add_or(IsRightSingleQuota())

    def run(self, tok: Sequence) -> bool:
        if self.is_right_quota(tok):
            if tok[tok.i - 1] in Symbols.end_symbols.value:
                return True
        return False


class IsNearestLeftQuota(Condition):
    def __init__(self, name='IsNearestRightQuota', reverse: bool = False):
        """
        case  'he said. "... ' > ['he said. ','"...']
        :param name:
        :param reverse:
        """
        super(IsNearestLeftQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.get_right_nearest_tok()
        if tok in Symbols.quotation_left.value or tok in Symbols.s_quota_left.value:
            return True
        if (seq.quota_en == 0 and tok in Symbols.quotation_en.value) \
                or (seq.s_quota_en == 0 and tok in Symbols.s_quota_en.value):
            return True
        return False


# --zh-- #
class IsNextSymbol(Condition):
    def __init__(self, name: str = 'IsNextSymbol', reverse: bool = False):
        super(IsNextSymbol, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        next = tok.get_right()
        return next in Symbols.end_symbols.value


class IsNextAllSymbol(Condition):
    def __init__(self, name: str = 'IsNextAllSymbol', reverse: bool = False):
        super(IsNextAllSymbol, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        next = tok.get_right()
        return next in Symbols.all_symbols()


class IsNextLeftQuota(Condition):
    def __init__(self, length: int = 2, name: str = 'IsNextLeftQuota', reverse: bool = False):
        super(IsNextLeftQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        next = seq.get_right()
        cut_list = Symbols.comma.value + Symbols.s_quota_right.value + Symbols.quotation_right.value + Symbols.quotation_en.value
        # print(seq.current_token, next, next in Symbols.quotation_left.value)
        if (seq.current_token not in cut_list) and (seq.current_token != ' '):
            return False
        if next in Symbols.quotation_left.value:
            return True
        if seq.quota_en == 0 and next in Symbols.quotation_en.value:
            return True
        return False


class IsNextLeftBracket(Condition):
    def __init__(self, name: str = 'IsNextLeftBracket', reverse: bool = False):
        super(IsNextLeftBracket, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        next = seq.get_right()
        if next in list('(（'):
            return True
        return False


class IsRightBracket(Condition):
    def __init__(self, name: str = 'IsRightBracket', reverse: bool = False):
        super(IsRightBracket, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        next = seq.get_right()
        if seq.current_token in list(')）') and next not in Symbols.all_symbols():
            return True
        return False


class IsCommaStickWithQuota(Condition):
    def __init__(self, name: str = 'IsCommaStickWithQuota', reverse: bool = False):
        super(IsCommaStickWithQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.current_token
        next = seq.get_right()
        # print(tok, next, (tok in Symbols.comma.value) and (
        #         (seq.quota_en == 1 and next in Symbols.quotation_en.value) or (next in Symbols.quotation_left.value)))
        if (tok in Symbols.comma.value) and (
                (seq.s_quota_en == 1 and next in Symbols.s_quota_en.value) or
                (seq.quota_en == 1 and next in Symbols.quotation_en.value) or
                (next in Symbols.quotation_left.value)):
            return True
        return False


# class IsQuotaStickWithSay(Condition):
#     def __init__(self, name: str = 'IsQuotaStickWithSay', reverse: bool = False):
#         super(IsQuotaStickWithSay, self).__init__(name, reverse)
#
#     def run(self, seq: Sequence) -> bool:
#         tok = seq.current_token
#         next = seq.get_right()
#         # print(tok, next, (tok in Symbols.comma.value) and (
#         #         (seq.quota_en == 1 and next in Symbols.quotation_en.value) or (next in Symbols.quotation_left.value)))
#         if (next in Symbols.comma.value) and (
#                 (seq.s_quota_en == 0 and tok in Symbols.s_quota_en.value) or
#                 (seq.quota_en == 0 and tok in Symbols.quotation_en.value) or
#                 (tok in Symbols.quotation_right.value) or
#                 (tok in Symbols.s_quota_right.value)):
#             return True
#         return False


class IsColonStickWithQuota(Condition):
    def __init__(self, name: str = 'IsColonStickWithQuota', reverse: bool = False):
        super(IsColonStickWithQuota, self).__init__(name, reverse)

    def run(self, seq: Sequence) -> bool:
        tok = seq.current_token
        next = seq.get_right()
        # print(tok, next, (tok in Symbols.comma.value) and (
        #         (seq.quota_en == 1 and next in Symbols.quotation_en.value) or (next in Symbols.quotation_left.value)))
        if (tok in Symbols.colon.value) and (
                (seq.quota_en == 1 and next in Symbols.quotation_en.value) or (next in Symbols.quotation_left.value)):
            return True
        return False


class IsNextLeftQuotaGreater(Condition):
    def __init__(self, name: str = 'IsNextLeftQuotaGreater', theta: int = 0, reverse: bool = False):
        super(IsNextLeftQuotaGreater, self).__init__(name, reverse)
        self.theta = theta

    def run(self, seq: Sequence) -> bool:
        next = seq.get_right()
        # print(seq.current_token, next, next in Symbols.quotation_left.value)
        if next in Symbols.quotation_left.value and seq.quota_left + seq.quota_right > self.theta:
            # seq.quota_left -= 1
            return True
        return False


class IsEndSymbolBeforeQuota(Condition):
    def __init__(self, name: str = 'IsEndSymbolBeforeQuota', reverse: bool = False):
        super(IsEndSymbolBeforeQuota, self).__init__(name, reverse)

    def run(self, tok: Sequence) -> bool:
        pre = tok.get_left()
        if pre in Symbols.end_symbols.value and (
                (tok.quota_en == 0 and tok.current_token in Symbols.quotation_right.value) or
                (tok.current_token in Symbols.s_quota_right.value) or
                (tok.current_token in Symbols.quotation_en.value) or
                (tok.s_quota_en == 0 and tok.current_token in Symbols.s_quota_en.value)):
            return True
        return False


class IsBeforeQuote(Condition):
    def __init__(self, name: str = 'IsBeforeQuote', reverse: bool = False):
        super(IsBeforeQuote, self).__init__(name, reverse)
        self.pattern1 = re.compile(r'.*\[[1-9]{1,2}\].*')
        self.pattern2 = re.compile(r'.*\[[1-9]0\].*')

    def run(self, tok: Sequence) -> bool:
        string = tok.get_right_interval(length=6)
        if self.pattern1.match(string) or self.pattern2.match(string):
            return True
        return False


class IsNextSymbolAfterQuotaLarger(Condition):
    def __init__(self, name: str = 'IsNextSymbolAfterQuotaLarger', min_length: int = 3, length: int = 10,
                 reverse: bool = False):
        super(IsNextSymbolAfterQuotaLarger, self).__init__(name, reverse)
        self.length = length
        self.min_length = min_length

    def run(self, tok: Sequence) -> bool:
        if (
                (tok.quota_en == 0 and tok.current_token in Symbols.quotation_right.value) or
                (tok.current_token in Symbols.s_quota_right.value) or
                (tok.current_token in Symbols.quotation_en.value) or
                (tok.s_quota_en == 0 and tok.current_token in Symbols.s_quota_en.value)):
            right_i = left_i = tok.i
            number = 0
            special_symbol = 0
            left_quota = 0
            not_quota_len = False
            stop = False
            for _ in range(15):
                right_i += 1
                left_i -= 1
                if tok[right_i] == ' ':
                    continue
                if not stop:
                    number += 1
                if tok[left_i] not in Symbols.all_symbols() and (1 - not_quota_len):
                    left_quota += 1
                if (1 - not_quota_len) and abs(ord(tok[left_i]) - ord(tok.current_token)) <= 1:
                    not_quota_len = True
                if tok[right_i] in Symbols.all_symbols() and (1 - stop):
                    special_symbol += 1
                    stop = True
            tok.get_left_interval()
            control1 = True
            if not_quota_len:
                control1 = (left_quota - 1 >= self.min_length)
            control2 = True
            if (tok.get_left() in Symbols.all_symbols()) and (tok.get_left() not in Symbols.end_symbols.value):
                control2 = False
            if number - 1 > self.length and (special_symbol != number) and control1 and control2:
                return True
        return False


class IsNextQuotaSentenceGreater(Condition):
    def __init__(self, length: int = 3, name: str = 'IsNextQuotaSentenceGreater', reverse: bool = False):
        super(IsNextQuotaSentenceGreater, self).__init__(name, reverse)
        self.length = length

    def run(self, tok: Sequence) -> bool:
        right_quota = Symbols.s_quota_right.value + Symbols.quotation_right.value + Symbols.quotation_en.value
        left_quota = Symbols.s_quota_left.value + Symbols.quotation_left.value + Symbols.quotation_en.value
        step = 1
        next = tok[tok.i + step]
        while next == ' ':
            next = tok[tok.i + step]
            step += 1

        if tok.current_token in right_quota and next in left_quota:
            right_i = tok.i + 1
            left_i = tok.i
            left_sentence_length = right_sentence_length = self.length + 1
            for _ in range(self.length):
                right_i += 1
                left_i -= 1
                if tok[right_i] in right_quota:
                    right_sentence_length = right_i - (tok.i + 1)
                if tok[left_i] in left_quota:
                    left_sentence_length = tok.i - left_i
            if min(right_sentence_length, left_sentence_length) > self.length:
                return True
            else:
                return False
        return True
