# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/1/27 2:38 PM
# LAST MODIFIED ON:
# AIM:

import pandas

from sentence_spliter_old.spliter import cut_to_sentences_en

path = '测试250.xlsx'
data = pandas.read_excel(path)

out =[] 
for sentence in data['原始']:
    sub = cut_to_sentences_en(sentence)
    out.append('\n\n'.join(v.strip() for v in sub))

data['策略：平均子句长度惩罚'] = out

data.to_excel('测试250.xlsx')

print('done')