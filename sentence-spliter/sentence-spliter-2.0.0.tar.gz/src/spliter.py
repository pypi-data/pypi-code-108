# -*- coding:utf-8 -*-
import re
import os
import sys


class Spliter:

    def __init__(self, option):
        """
        :param option: 决定是中文还是英文
        """
        self.option = option
        self.end_flags = ['?', '!', '.', '…', '？', '！', '。', '……']  # 句子结束符号，包括中文和英文的
        self.sentences = []
        self.flag = 0
        self.flag_quote = 0
        self.tmp_char = ''
        # -- parameter -- #

    # -- filter -- #

    # -- sentences segmentation -- #
    def cut_to_sentences(self, paragraph, verbose: bool = True):
        """
        切分段落
        :param verbose:
        :param paragraph:
        :return: 切分好的list
        """
        self.sentences = []
        self.tmp_char = ''
        if len(paragraph) == 0:
            return []
        total_len = len(paragraph)
        for index, char in enumerate(paragraph):
            if verbose:
                percent = float(index) / total_len * 100.0
                sys.stdout.write('\rprocess sentence cut : {0:.2g}%'.format(percent))
            self._do_cut(char, index, paragraph)
        outputs = []
        outputs.extend(sente.replace('\n', '') for sente in self.sentences if len(sente) > 1)  # 去掉空值和长度为1的
        return outputs

    def _do_cut(self, char, index, paragraph):
        """
        切分的状态机，再封装各个情况，每个if能拆解为函数
        :param index:
        :param char:
        :param paragraph:
        """
        self.tmp_char += char
        if self._last_char(index, paragraph) is True:  # 判断是否已经到了段落最后一个字符
            return
        if char == '”' or char == '"':
            self.flag = 0
            if paragraph[index + 1] == '，' or paragraph[index + 1] == ',':
                pass
            else:
                self.sentences.append(self.tmp_char)
                self.tmp_char = ''

        if char == '“' or char == '"' and self.flag_quote == 0:
            start_char = self.quota_begin()
            end_char = self.quota_end()
            if self.match_quota_sentences(start_char, end_char, paragraph[index:]) is True:
                self.flag = 1
                self.flag_quote = 1
        if self._end_char(char) == True and self.flag == 0:  # 判断此字符是否为结束符号
            if self._demical_char(char, index, paragraph) is True:  # 判断是否是小数
                return
            elif paragraph[index + 1] not in self.end_flags:
                self.sentences.append(self.tmp_char)
                self.tmp_char = ''

    def match_quota_sentences(self, start_char, end_char, sentence):
        """
        匹配有引号的句子
        :param start_char:
        :param end_char:
        :param sentence:
        :return: True/False 是否匹配到有引号的句子
        """
        pattern_str = r'%s(.+?)%s' % (start_char, end_char)
        p = re.compile(pattern_str, re.IGNORECASE)
        m = re.match(p, sentence)
        if m:
            return True
        else:
            return False

    def quota_begin(self):
        """
        引号开始
        :return:start_char
        """
        if self.option == 1:
            start_char = '“'
        else:
            start_char = '"'
        return start_char

    def quota_end(self):
        """
        引号结束
        :return:end_char
        """
        if self.option == 1:
            end_char = '”'
        else:
            end_char = '"'
        return end_char

    def _last_char(self, index, paragraph):
        """
        是否是段落最后一个字符
        :param index:
        :param paragraph:
        :return: True/False
        """
        if (index + 1) == len(paragraph):
            self.sentences.append(self.tmp_char)
            return True
        else:
            return False

    def _end_char(self, char):
        """
        是否是划分句子的字符
        :param char:
        :return: True/False
        """
        if char in self.end_flags:
            return True
        else:
            return False

    def _demical_char(self, char, index, paragraph):
        """
        是否是小数
        :param char:
        :param index:
        :param paragraph:
        :return: True/False
        """
        if char == '.' and paragraph[index - 1].isdigit() and paragraph[index + 1].isdigit():
            return True
        else:
            return False
