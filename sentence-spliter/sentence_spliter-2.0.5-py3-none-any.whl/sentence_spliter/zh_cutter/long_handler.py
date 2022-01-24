# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/24 3:06 PM
# LAST MODIFIED ON:
# AIM:
import os
import re
import pathlib

from sentence_spliter.architect.graph_component import Graph, Operation
import sentence_spliter.zh_cutter.condition as cond
import sentence_spliter.zh_cutter.operation as opt
from sentence_spliter.zh_cutter.zh_sequence import Sequence, SequenceABC
from sentence_spliter.zh_cutter.symbol import Symbols
from sentence_spliter.utility.file_opt import read_file
from sentence_spliter.utility.trie import Trie

WEIGHT_PATH = os.path.join(str(pathlib.Path(__file__).absolute().parent), 'weights_list.txt')


def get_int_key(dictionary: dict):
    for key in dictionary.keys():
        if type(key) == int:
            return key
    else:
        return None


class IntegrityCut(Operation):
    def __init__(self, name: str = 'IntegrityCut', min_len: int = 6, max_len: int = 40):
        """
        尽量不在句内拆分, 切分引号啥的
        """
        super(IntegrityCut, self).__init__(name)
        # -- set operation -- #
        self.back_sentence_start = opt.BackToSentenceStart()
        # -- set condition -- #
        self.is_end_symbol = cond.IsEndSymbol()\
            .add_and(cond.IsNextLeftBracket(reverse=True))\
            .add_and(cond.IsBeforeQuote(reverse=True))\
            .add_or(cond.IsNextLeftQuota())\
            .add_or(cond.IsNextSymbolAfterQuotaLarger(length=4, min_length=3)) \
            .add_or(cond.IsRightBracket())
        self.not_in_whitelist = cond.TokenInWhiteList(reverse=True)
        self.is_all_close = cond.IsBracketClose().add_and(cond.IsQuotaClose()).add_and(cond.IsSingleQuotaClose())
        self.next_capital = cond.NextStartWithCapital().add_or(cond.NextStartWithNum())
        self.is_short_sentence = cond.IsShortSentence(min_length=min_len)
        self.is_sentence_dash = cond.IsSentenceDash()
        self.is_long_sentence = cond.IsLongSentence(max_length=max_len)

        self.right_quota = Symbols.quotation_right.value + Symbols.s_quota_right.value + \
                           Symbols.s_quota_en.value + Symbols.quotation_en.value
        self.is_not_comma_stick_quota = self.is_not_comma_stick_quota = cond.IsCommaStickWithQuota(
            name='NotCommaStickWithQuota', reverse=True)
        self.not_number_dot = cond.IsNumberDot(name='NotNumberDot', reverse=True)
        self.is_not_symbol = cond.IsNextSymbol(name='NotNextSymbol', reverse=True).add_or(cond.IsNextLeftQuota())
        self.is_not_colon_stick_quota = cond.IsColonStickWithQuota(name='NotColonStickWithQuota', reverse=True)

    def run(self, seq: Sequence) -> None:
        end_pos = seq.i
        self.back_sentence_start.run(seq)

        for idx, _ in enumerate(seq):
            if self.is_short_sentence(seq):
                continue
            if seq.i >= end_pos:
                break

            if self.is_end_symbol(seq) \
                    and self.is_all_close(seq) \
                    and self.is_not_comma_stick_quota(seq) \
                    and self.is_not_colon_stick_quota(seq) \
                    and self.not_in_whitelist(seq) \
                    and not seq[seq.i + 1] in self.right_quota \
                    and self.not_number_dot(seq) \
                    and self.is_not_symbol:
                return
            # -- ?'   ?) 这两个case
            if (seq.current_token in self.right_quota) or (seq.current_token in Symbols.bracket_right.value):
                if seq[seq.i - 1] in Symbols.end_symbols.value:  # 优先切这里
                    return
                elif seq[seq.i - 1] in Symbols.semicolon.value:  # 其次切这里
                    return

            # 有分号
            if seq.current_token in Symbols.semicolon.value:
                return
            # if self.is_sentence_dash(seq):
            #     return


class IntSentenceCut(Operation):
    def __init__(self, name: str = 'IntSentenceCut', min_len: int = 6, max_len: int = 40):
        """
        句子内部切分
        """
        super(IntSentenceCut, self).__init__(name)
        # -- set operation -- #
        self.back_sentence_start = opt.BackToSentenceStart()
        self.cut = opt.Cut()
        # -- set condition -- #
        self.is_quota_close = cond.IsQuotaClose().add_and(cond.IsSingleQuotaClose())
        self.is_bracket_close = cond.IsBracketClose()
        self.is_end_symbol = cond.IsEndSymbol().add_and(cond.IsNextLeftBracket(reverse=True))\
            .add_and(cond.IsBeforeQuote(reverse=True))\
            .add_and(cond.TokenInWhiteList(reverse=True))\
            .add_or(cond.IsNextLeftQuota())\
            .add_or(cond.IsNextSymbolAfterQuotaLarger(length=4, min_length=3)) \
            .add_or(cond.IsRightBracket())
        self.is_next_capital = cond.NextStartWithCapital().add_or(cond.NextStartWithNum())
        self.is_short_sentence = cond.IsShortSentence(min_length=min_len)

        self.is_right_quota = cond.IsRightQuota().add_or(cond.IsRightSingleQuota())
        self.is_blank = cond.IsBlank()
        self.max_len = max_len
        self.is_right_quota = cond.IsRightQuota().add_or(cond.IsRightSingleQuota())
        # -- load weight_list -- #
        self.weight = self.load_weight_list()

        self.all_quota = Symbols.all_quota.value + Symbols.all_s_quota.value
        self.is_not_symbol = cond.IsNextSymbol(name='NotNextSymbol', reverse=True).add_or(cond.IsNextLeftQuota())
        self.is_not_all_symbol = cond.IsNextAllSymbol(name='NotNextAllSymbol', reverse=True).add_or(
            cond.IsNextLeftQuota())
        # self.is_not_next_bracket = cond.IsNextLeftBracket(name='NotNextLeftBracket', reverse=True)

    @staticmethod
    def load_weight_list() -> Trie:
        tree = Trie('<root>')
        weight_list = [v for v in read_file(WEIGHT_PATH).splitlines() if v]
        for tokens in weight_list:
            tokens = tokens.split()
            tokens[-1] = int(tokens[-1])
            tree.add_phrase(tokens)
        return tree

    def run(self, seq: Sequence) -> None:
        max_score = -1
        best_i = -1
        length = seq.i - seq.sentence_start
        end_pos = seq.i
        half_len = max(length // 2, 1)
        self.back_sentence_start.run(seq)
        traverse_trie = False
        tree = self.weight
        split_i = seq.i
        weight = -1000
        n_word = 0
        for idx, _ in enumerate(seq):
            position_penalty = 1 - abs(idx - half_len) / half_len

            if seq.i >= end_pos:
                break

            if traverse_trie:
                score = get_int_key(tree.children)
                if score is not None:
                    weight += position_penalty
                    traverse_trie = False
                elif seq.current_token in tree:
                    tree = tree[seq.current_token]
                else:
                    tree = self.weight
                    traverse_trie = False
                    weight = -1000
            else:
                n_word = seq.n_words

            if self.is_blank(seq):
                continue
            # -- get comma
            if (seq.current_token in Symbols.comma.value and not seq[seq.i + 1] in self.all_quota) or \
                    (seq.current_token in Symbols.bracket_right.value and self.is_quota_close(seq) and
                     self.is_not_all_symbol(seq)) or \
                    (self.is_quota_close(seq) and self.is_bracket_close(seq) and self.is_right_quota(seq) and seq[
                        seq.i - 1] not in Symbols.comma.value) or \
                    seq.current_token in Symbols.colon.value:
                if not self.is_short_sentence(seq):
                    weight = 0.5 + position_penalty
                    split_i = seq.i
                    traverse_trie = True

            if self.is_end_symbol(seq) and self.is_not_symbol(seq) and 1 < n_word < self.max_len and not self.is_short_sentence(seq):
                score = 1
                if self.is_quota_close(seq) and self.is_bracket_close(seq):
                    score += 1
                weight = score + position_penalty
                split_i = seq.i

            if (self.is_right_quota(seq) or seq.current_token in Symbols.bracket_right.value) \
                    and 1 < n_word < self.max_len \
                    and seq.get_left_nearest_tok() not in Symbols.all_symbols() \
                    and re.match(r'^\s+$', seq[seq.i + 1]):
                score = 1
                if self.is_quota_close(seq) and self.is_bracket_close(seq):
                    score += 1
                weight = 1 + position_penalty
                split_i = seq.i

            if weight > max_score:
                best_i = split_i
                max_score = weight
        if best_i > 0:
            seq.i = best_i
            self.cut.run(seq)


class LongHandler(Operation):
    def __init__(self, name: str = 'LongHandler', min_len: int = 6, max_len: int = 40):
        super(LongHandler, self).__init__(name)
        # -- set operation -- #
        self.integrity_cut = IntegrityCut(min_len=min_len, max_len=max_len)
        self.in_sentence_cut = IntSentenceCut(max_len=max_len, min_len=min_len)
        self.cut = opt.Cut()
        # -- set condition -- #
        self.is_long_sentence = cond.IsLongSentence(max_length=max_len)

    def run(self, seq: Sequence) -> None:
        org_i = seq.i
        org_n_word = seq.n_words  # 防止死循环
        self.integrity_cut.run(seq)
        if org_i == seq.i:  # self.is_long_sentence(seq):
            self.in_sentence_cut.run(seq)
            # -- 防止死循环 -- #
            if org_i == seq.i:  # self.is_long_sentence(seq):
                seq.i = org_i
                seq.n_words = org_n_word
        else:
            return self.cut.run(seq)
