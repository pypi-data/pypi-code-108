# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/1/21 3:53 PM
# LAST MODIFIED ON:
# AIM:

from sentence_spliter_old.spliter import cut_to_sentences_en

with open('file.txt' , 'r') as f:
    sentence = f.read().strip()

out = cut_to_sentences_en(sentence)

print('\n\n'.join(v.strip() for v in out))
