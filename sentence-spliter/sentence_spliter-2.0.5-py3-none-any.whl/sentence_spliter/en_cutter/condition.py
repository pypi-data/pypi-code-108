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
from sentence_spliter.en_cutter.symbol import Symbols
from sentence_spliter.en_cutter.en_sequence import Sequence
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
        self.pattern = re.compile('^\d+(.\d+)*$')

    def run(self, tok: Sequence) -> bool:
        if tok.current_token == '.' and self.pattern.match(tok[tok.i-1]):
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
        return tok.n_words > self.max_length


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
