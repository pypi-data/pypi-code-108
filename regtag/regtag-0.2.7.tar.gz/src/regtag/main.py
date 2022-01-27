#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .renumbers import re_num_list
from .renumberscales import re_number_scale_list
from .redate import re_date_list
from .reid import re_id_list
from .reabb import list_word_abb
from .reoov import format_word, check_oov_word
from .clean_text import clean_line
import re
# from nltk import word_tokenize


def get_re_idx(re_str, src_txt):
    src_txt = src_txt.lower()
    p_list = [
        (re.compile("^(" + re_str + ")\s"), 1),
        (re.compile("\s(" + re_str + ")$"), 1),
        (re.compile("(?=(\s(" + re_str + ")\s))"), 2),
        (re.compile("^(" + re_str + ")$"), 1),
    ]
    dict_result = dict({})
    for (p, idx) in p_list:
        # print(p, idx)
        # print(p, list(p.finditer(src_txt)))
        for m in p.finditer(src_txt):
            dict_result["{}-{}".format(m.start(idx), len(m.group(idx)))] = m.group(idx)
    return dict_result


def extract_word_tag(txt, txt_tag):
    phrases = []
    phrases_tags = []

    current_tag = 'O'
    phrase = []
    for char, char_tag in zip(list(txt), txt_tag):
        if char_tag.split('-')[-1] != current_tag:
            if len(phrase) > 0:
                phrases.append(''.join(phrase))
                phrases_tags.append(current_tag)
            phrase = [char]
            current_tag = char_tag.split('-')[-1]
        else:
            phrase.append(char)
    if len(phrase) > 0:
        phrases.append(''.join(phrase))
        phrases_tags.append(current_tag)

    words, word_tags = [], []
    for w, t in zip(phrases, phrases_tags):
        list_words = w.strip().split()
        words.extend(list_words)
        if t == 'O':
            word_tags.extend(['O'] * len(list_words))
        else:
            word_tags.append('B-{}'.format(t))
            word_tags.extend(['I-{}'.format(t)] * (len(list_words) - 1))

    return words, word_tags


def tagging(txt, debug=False):
    txt = clean_line(txt)
    txt_tag = ['O'] * len(txt)

    # number
    regex_numer = []
    for re_num in re_num_list:
        result = get_re_idx(re_num, txt)
        if len(result) > 0:
            regex_numer.append(result)
    for rel in regex_numer:
        for pos in rel.keys():
            idx = int(pos.split('-')[0])
            len_item = int(pos.split('-')[1])
            txt_tag[idx] = 'B-number'
            for i in range(idx + 1, idx + len_item):
                txt_tag[i] = 'I-number'
    if debug:
        print(regex_numer)
    # date
    regex_date = []
    for re_date in re_date_list:
        result = get_re_idx(re_date, txt)
        if len(result) > 0:
            regex_date.append(result)

    for rel in regex_date:
        for pos in rel.keys():
            idx = int(pos.split('-')[0])
            len_item = int(pos.split('-')[1])
            txt_tag[idx] = 'B-date'
            for i in range(idx + 1, idx + len_item):
                txt_tag[i] = 'I-date'
    if debug:
        print(regex_date)
    # number + scale
    regex_numscale = []
    for re_num_scale in re_number_scale_list:
        result = get_re_idx(re_num_scale, txt)
        if len(result) > 0:
            regex_numscale.append(result)
    for rel in regex_numscale:
        for pos in rel.keys():
            idx = int(pos.split('-')[0])
            len_item = int(pos.split('-')[1])
            txt_tag[idx] = 'B-numscale'
            for i in range(idx + 1, idx + len_item):
                txt_tag[i] = 'I-numscale'
    if debug:
        print(regex_numscale)
    # id
    regex_id = []
    for re_id in re_id_list:
        result = get_re_idx(re_id, txt)
        if len(result) > 0:
            regex_id.append(result)
    if debug:
        print(regex_id)
    for rel in regex_id:
        for pos in rel.keys():
            idx = int(pos.split('-')[0])
            len_item = int(pos.split('-')[1])
            if list(set(txt_tag[idx:idx + len_item])) == ['O']:
                txt_tag[idx] = 'B-id'
                for i in range(idx + 1, idx + len_item):
                    txt_tag[i] = 'I-id'
    # OOV
    chars = []
    word_idx = 0
    oov_words = []
    for idx, char in enumerate(list(txt)):
        if char != ' ':
            chars.append(char)
        else:
            if len(chars) > 0:
                word = ''.join(chars)
                if format_word(word) in list_word_abb:
                    oov_words.append(word)
                    if list(set(txt_tag[word_idx:word_idx + len(chars)])) == ['O']:
                        txt_tag[word_idx] = 'B-abbrev'
                        for i in range(word_idx + 1, word_idx + len(chars)):
                            txt_tag[i] = 'I-abbrev'
                else:
                    # check oov
                    if check_oov_word(word):
                        oov_words.append(word)
                        if list(set(txt_tag[word_idx:word_idx + len(chars)])) == ['O']:
                            txt_tag[word_idx] = 'B-oov'
                            for i in range(word_idx + 1, word_idx + len(chars)):
                                txt_tag[i] = 'I-oov'
            chars = []
            word_idx = idx + 1
    if len(chars) > 0:
        word = ''.join(chars)
        if format_word(word) in list_word_abb:
            oov_words.append(word)
            if list(set(txt_tag[word_idx:word_idx + len(chars)])) == ['O']:
                txt_tag[word_idx] = 'B-abbrev'
                for i in range(word_idx + 1, word_idx + len(chars)):
                    txt_tag[i] = 'I-abbrev'
        else:
            # check oov
            if check_oov_word(word):
                oov_words.append(word)
                if list(set(txt_tag[word_idx:word_idx + len(chars)])) == ['O']:
                    txt_tag[word_idx] = 'B-oov'
                    for i in range(word_idx + 1, word_idx + len(chars)):
                        txt_tag[i] = 'I-oov'

    if debug:
        print(oov_words)
    return extract_word_tag(txt, txt_tag)


if __name__ == "__main__":
    input_text = 'Tiền thưởng U23 Việt Nam vượt mốc 23.231 tỷ đồng, Thành công tại giải U23 châu Á giúp tuyển U23 Việt Nam đón cơn mưa tiền thưởng, hiện vật và dịch vụ.'
    # input_text = '152/2017/NĐ-CP của ttcp 13 kb ngày 9/10/2021 -87,5 wh'
    # input_text = ' '.join(word_tokenize(input_text))
    print(input_text)
    tags = tagging(input_text)
    for t, p_i in zip(*tags):
        print(t, p_i)
