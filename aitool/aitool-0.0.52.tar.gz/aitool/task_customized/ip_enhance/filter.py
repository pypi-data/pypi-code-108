# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

"""
import os
import warnings
import logging
import re
from typing import Dict, Union, List, Any, NoReturn
from aitool.datasets import PATH as DATA_PATH
from aitool import is_file_exist, load_lines, prepare_data, load_json


chinese_family_name = set()
File_Bag = ['https://pcg-xyj-1258344701.cos.ap-guangzhou.myqcloud.com/aitool/words.zip', os.path.join(DATA_PATH, 'nlp', 'words')]
File_Chinese_Family_Name = os.path.join(DATA_PATH, 'nlp', 'words', 'Names', 'Chinese_family_name.txt')


def has_family_name(name: str) -> bool:
    if not chinese_family_name:
        if not is_file_exist(File_Chinese_Family_Name):
            prepare_data(*File_Bag, packed=True)
        for item in load_lines(File_Chinese_Family_Name):
            chinese_family_name.add(item)
    if len(name) > 0 and name[0] in chinese_family_name:
        return True
    return False


word_common = set()
DIR_THUOCL = os.path.join(DATA_PATH, 'nlp', 'words', 'THUOCL')
FILE_XINHUA_CI = os.path.join(DATA_PATH, 'nlp', 'words', 'XINHUA', 'ci.json')

def init_word_common(threshold: int = 10) -> NoReturn:
    if not is_file_exist(DIR_THUOCL) or not is_file_exist(FILE_XINHUA_CI):
        prepare_data(*File_Bag, packed=True)
    files = os.listdir(DIR_THUOCL)
    for file in files:
        with open(os.path.join(DIR_THUOCL, file), 'r') as fin:
            for line in fin:
                w, f = line.strip().split('\t')
                if eval(f) > threshold:
                    word_common.add(w)
    data = load_json(FILE_XINHUA_CI)
    for line in data:
        word_common.add(line['ci'])


def is_common_word(text: str) -> bool:
    if not word_common:
        init_word_common()
    if text in word_common:
        return True
    return False


word_stop = set()
FILE_STOPWORDS = os.path.join(DATA_PATH, 'nlp', 'words', 'stopwords.txt')


def init_word_stop() -> NoReturn:
    with open(FILE_STOPWORDS, 'r') as fin:
        for line in fin:
            word = line.strip()
            word_stop.add(word)


def is_stop_word(text: str) -> bool:
    if not word_stop:
        init_word_stop()
    if text in word_stop:
        return True
    return False


relationship_title = {}
FILE_RELATIONSHIP = os.path.join(DATA_PATH, 'nlp', 'words', 'Names', 'relationship.txt')


def init_relationship_title() -> NoReturn:
    if not is_file_exist(FILE_RELATIONSHIP):
        prepare_data(*File_Bag, packed=True)
    relationship_title_addition = {'店长', '法师', '醫生', '大力士', '护士', '父亲', '天后', '教练', '保安', '计师', '管事',
                                   '知事', '道长', '妃', '母亲', '头目', '乞丐', '妻', '局长', '官员', '', '', '', '', '',
                                   '', '', '', '', '', '', '', '', '', '', '', '', '', ''}
    data = set(load_lines(FILE_RELATIONSHIP)) | relationship_title_addition
    for item in data:
        item_len = len(item)
        if item_len not in relationship_title:
            relationship_title[item_len] = set()
        relationship_title[item_len].add(item)


def is_relationship_title(text: str) -> bool:
    if not relationship_title:
        init_relationship_title()
    text_len = len(text)
    for title_len, title_items in relationship_title.items():
        if title_len + 1 != text_len:
            continue
        if text[:-1] in title_items or text[1:] in title_items:
            return True
    return False


def is_contains_english(text: str) -> bool:
    for c in text:
        _ord = ord(c)
        if 65 <= _ord <= 90 or 97 <= _ord <= 122:
            return True
    return False


cut_until_char_delimiter = set('(（[〔【')


def cut_until_char(text: str, delimiter: Union[tuple, str, list] = cut_until_char_delimiter) -> str:
    for index, char in enumerate(text):
        if char in delimiter:
            return text[:index]
    return text


delete_char_discard = set(')〕－-”—.“《）')


def delete_char(text: str, discard: Union[tuple, str, list] = delete_char_discard):
    new_text = ''
    for char in text:
        if char not in discard:
            new_text += char
    return new_text


nick_name_prefix = set('小大老阿男女')
nick_name_postfix_1 = set('哥姐总')
nick_name_postfix_2 = set('甲乙丙丁戊己庚辛壬癸一二三四五六七八九十')


def is_nick_name(text: str, ) -> bool:
    if len(text) == 2:
        if text[0] in nick_name_prefix or text[-1] in nick_name_postfix_1:
            return True
        if text[0] in nick_name_postfix_2 or text[1] in nick_name_postfix_2:
            return True
    if len(text) == 3:
        if text[0] in nick_name_postfix_2 and text[1] in nick_name_postfix_2:
            return True
    return False


def is_contains_figure(text: str) -> bool:
    for char in text:
        if char.isdigit():
            return True
    return False


age_describes = ['童年', '老奶奶', '幼年', '老年', '少年', ]


def delete_age_describe(text: str) -> str:
    for describe in age_describes:
        text = text.replace(describe, '')
    return text


def is_contains_chinese(strs) -> bool:
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fff':
            return True
    return False


def is_all_chinese(text: str) -> bool:
    for char in text:
        if (not is_contains_chinese(char)) and (char not in '·‧：∙:'):
            return False
    return True


black_name = {'未知', '收废品员', '开发商', '理发师', '小棉袄', '大高个', '地下党', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '',
              '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
              '', '', '', '', ''}


def is_black_name(text: str) -> bool:
    warnings.warn("is_black_name will be deprecated "
                  "because black_name should be disassemble to relationship_title", DeprecationWarning)
    if text in black_name:
        return True
    return False


def clean_role(text: str) -> (str, int):
    score = 10
    text = cut_until_char(text)
    text = delete_char(text)
    text = delete_age_describe(text)
    if not text:
        return '', -100
    if not is_contains_chinese:
        return '', -100
    if has_family_name(text):
        score -= 1
    if is_common_word(text):
        score -= 1
    if is_relationship_title(text):
        score -= 1
    if is_contains_english(text):
        score -= 1
    if is_nick_name(text):
        score -= 1
    if is_contains_figure(text):
        score -= 1
    if is_all_chinese(text):
        score += 1
    if is_black_name(text):
        score -= 1
    logging.info('{}, {}'.format(text, score))
    return text, score


def clean_alias(text: str) -> (str, int):
    score = 13
    if not text:
        return '', -100
    if not is_contains_chinese:
        score -= 5
    if is_common_word(text):
        score -= 5
    if is_relationship_title(text):
        score -= 3
    if is_contains_english(text):
        score -= 1
    if is_nick_name(text):
        score -= 1
    if is_contains_figure(text):
        score -= 1
    if is_all_chinese(text):
        score += 1
    logging.info('{}, {}'.format(text, score))
    return text, score

import sys
from unicodedata import category
punctuation_chars = set([chr(i) for i in range(sys.maxunicode)
                             if category(chr(i)).startswith("P")])
punctuation_chars |= set(['`', ' '])


def is_punctuation(char):
    return char in punctuation_chars


def select_nested_text(
        text: str,
        deep_add: tuple = ('《',),
        deep_reduce: tuple = ('》',)
) -> str:
    new_text = ''
    deep = 0
    for char in text:
        if char in deep_reduce and deep > 0:
            deep -= 1
        if deep != 0:
            new_text += char
        if char in deep_add:
            deep += 1
    return new_text


def delete_nested_text(
        text: str,
        deep_add: tuple = ('(', '（', '[', '【',),
        deep_reduce: tuple = (')', '）', ']', '】',)
) -> str:
    # 删除以（）、()修饰的嵌套成分
    new_text = ''
    deep = 0
    for char in text:
        if char in deep_add:
            deep += 1
        if deep == 0:
            new_text += char
        if char in deep_reduce and deep > 0:
            deep -= 1
    return new_text


pattern_1 = re.compile(r'(全|第)[1-90一二三四五六七八九十零〇]+(章|季|集|部分|部|卷)')
pattern_2 = re.compile(r'[:：]*[（([]*(结局一|结局二|结局三|法国版|完全版|剧场版|电影版|剧场剪辑版|印度版|合体版＋|合体版|重置版|合体剧场版|原版|正序版|精编版|粤语版|总集篇|电视剧版|电视剧|全集|动画版)[）)\]]*')
pattern_3 = re.compile(r'[1-90一二三四五六七八九十零〇]+$')


def get_core_ip(ip: str) -> str:
    ip = delete_nested_text(ip)
    ip = re.sub(pattern_1, '', ip)
    ip = re.sub(pattern_2, '', ip)
    ip = re.sub(pattern_3, '', ip)
    ip = ip.split(' ')[0]
    ip = ip.split('-')[0]
    return ip


def is_sub_ip(ip: str) -> bool:
    if re.search(pattern_1, ip):
        return True
    if re.findall(pattern_2, ip):
        return True
    if re.findall(pattern_3, ip):
        return True
    return False


if __name__ == '__main__':
    print(has_family_name('项羽'))
    print(has_family_name('翼德'))
    print(is_contains_english('小bird'))
    print(is_contains_english('项羽'))
    print(cut_until_char('A(B'))
    print(cut_until_char('【AB'))
    print(is_common_word('汽车'))
    print(is_common_word('唐三'))
    print(is_relationship_title('张老师'))
    print(is_relationship_title('唐三'))
    print(clean_role('汽车'))
    print(clean_role('唐三'))
    print(clean_role('唐三(主角)'))
    print(get_core_ip('托马斯和他的朋友们第十九部分'))
    print(get_core_ip('托马斯和他的朋友们19'))
    print(get_core_ip('托马斯和他的朋友们结局一'))
    print(get_core_ip('托马斯和他的朋友们(结局一))'))
    print(get_core_ip('托马斯 和他的朋友们:(结局一)'))
    print(get_core_ip('斗罗大陆（全14卷）'))
    print(get_core_ip('一'))
    print(is_sub_ip('托马斯和他的朋友们第十九部分'))
    print(is_sub_ip('托马斯和他的朋友们19'))
    print(is_sub_ip('托马斯和他的朋友们结局一'))
    print(is_sub_ip('托马斯和他的朋友们(结局一))'))
    print(is_sub_ip('托马斯 和他的朋友们:(结局一)'))
    print(is_sub_ip('斗罗大陆（全14卷）'))
    print(is_sub_ip('一'))
    print(select_nested_text('《xxxx》'))
    print(is_stop_word('的'))
    print(is_stop_word('匿'))
