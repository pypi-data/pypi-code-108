# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/16 10:18 AM
# LAST MODIFIED ON:
# AIM:
from sentence_spliter.architect.graph_component import Graph
import sentence_spliter.zh_cutter.condition as cond
import sentence_spliter.zh_cutter.operation as opt
from sentence_spliter.zh_cutter.long_handler import LongHandler, Operation


class SimpleLogic(Graph):
    def __init__(self, name: str = 'SimpleLogic'):
        super(SimpleLogic, self).__init__(name)

    def init_conditions(self):
        self.is_end_state = cond.IsEndState()
        self.is_next_left_quota = cond.IsNextLeftQuota()
        self.is_end_symbol = cond.IsEndSymbol()\
            .add_or(cond.IsNextLeftQuota())\
            .add_or(cond.IsNextSymbolAfterQuotaLarger(length=4))
        self.is_bracket_close = cond.IsBracketClose()
        self.is_quota_close = cond.IsQuotaClose().add_and(cond.IsSingleQuotaClose())
        self.not_in_white_list = cond.TokenInWhiteList(reverse=True)
        self.not_number_dot = cond.IsNumberDot(name='NotNumberDot', reverse=True)
        self.is_not_symbol = cond.IsNextSymbol(name='NotNextSymbol', reverse=True).add_or(cond.IsNextLeftQuota())
        self.is_not_comma_stick_quota = cond.IsCommaStickWithQuota(name='NotCommaStickWithQuota', reverse=True)
        self.is_next_left_quota_greater = cond.IsNextLeftQuotaGreater()
        self.is_not_colon_stick_quota = cond.IsColonStickWithQuota(name='NotColonStickWithQuota', reverse=True)
        # self.is_not_next_bracket = cond.IsNextLeftBracket(name='NotNextLeftBracket', reverse=True)

    def init_operations(self):
        self.init_state = opt.Indolent()
        self.end_state = opt.EndState()
        self.proceed_state = opt.Proceed()
        self.cut_state = opt.Cut()

    def build_logic(self) -> 'Operation':
        self.init_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.cut_state,
                       [self.is_next_left_quota_greater],
                       args=any) \
            .add_child(self.cut_state,
                       [self.is_quota_close, self.is_bracket_close, self.is_not_symbol, self.is_not_comma_stick_quota,
                        self.is_not_colon_stick_quota,
                        self.not_in_white_list, self.is_end_symbol, self.not_number_dot],
                       args=all) \
            .add_child(self.proceed_state)

        self.proceed_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.init_state)

        self.cut_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.init_state)
        return self.init_state


class LongShortLogic(Graph):
    def __init__(self, name: str = 'LongShortLogic', max_len: int = 40, min_len: int = 6, hard_max: int = -1):
        self.max_len = max_len
        self.min_len = min_len
        self.hard_max = hard_max
        super(LongShortLogic, self).__init__(name)

    def init_conditions(self):
        is_right_before_left_quota = cond.IsRightBeforeLeftQuota().add_and(cond.RightQuotaAfterEnd())

        self.is_end_state = cond.IsEndState()
        self.is_end_symbol = cond.IsEndSymbol().add_or(
            cond.IsNextLeftQuota()).add_or(
            cond.IsNextSymbolAfterQuotaLarger(length=4, min_length=3))
        self.is_bracket_close = cond.IsBracketClose()
        self.is_quota_close = cond.IsQuotaClose().add_and(cond.IsSingleQuotaClose())
        self.not_short_sentence = cond.IsShortSentence(name='NotShortSentence', reverse=True, min_length=self.min_len)
        self.is_long_sentence = cond.IsLongSentence(max_length=self.max_len)
        # if self.hard_max < 0:+
        self.is_max_long = cond.IsLongSentence(max_length=self.hard_max,
                                               name='harmax') if self.hard_max > 0 else self.is_long_sentence
        self.not_number_dot = cond.IsNumberDot(name='NotNumberDot', reverse=True)
        self.is_blank = cond.IsBlank()
        self.not_in_white_list = cond.TokenInWhiteList(reverse=True)
        self.is_not_symbol = cond.IsNextSymbol(name='NotNextSymbol', reverse=True).add_or(cond.IsNextLeftQuota())
        self.is_not_comma_stick_quota = cond.IsCommaStickWithQuota(name='NotCommaStickWithQuota', reverse=True)
        self.is_next_left_quota_greater = cond.IsNextLeftQuotaGreater()
        self.is_not_colon_stick_quota = cond.IsColonStickWithQuota(name='NotColonStickWithQuota', reverse=True)
        # self.is_not_next_bracket = cond.IsNextLeftBracket(name='NotNextLeftBracket', reverse=True)
        self.is_next_quota_sentence_greater = cond.IsNextQuotaSentenceGreater()

    def init_operations(self):
        self.init_state = opt.Indolent()
        self.reset_num_words = opt.ResetNumWords()
        self.end_state = opt.EndState(min_length=self.min_len)
        self.proceed_state = opt.Proceed()
        self.cut_state = opt.Cut()
        self.long_state = LongHandler(max_len=self.max_len, min_len=self.min_len)

    def build_logic(self) -> Operation:
        self.init_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.cut_state,
                       [self.is_next_left_quota_greater],
                       args=any) \
            .add_child(self.cut_state,
                       [self.is_quota_close, self.is_bracket_close, self.is_not_symbol, self.is_not_comma_stick_quota,
                        self.is_not_colon_stick_quota, self.is_next_quota_sentence_greater,
                        self.not_in_white_list, self.is_end_symbol, self.not_short_sentence, self.not_number_dot],
                       args=all) \
            .add_child(self.long_state, self.is_long_sentence) \
            .add_child(self.proceed_state)
        # .add_child(self.proceed_state, self.is_blank) \
        # .add_child(self.long_state, self.is_long_sentence) \
        # .add_child(self.proceed_state)

        self.proceed_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.init_state)

        self.cut_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.init_state)

        self.long_state \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.cut_state, self.is_max_long) \
            .add_child(self.reset_num_words, self.is_long_sentence) \
            .add_child(self.init_state)

        self.reset_num_words \
            .add_child(self.end_state, self.is_end_state) \
            .add_child(self.init_state)

        return self.init_state
