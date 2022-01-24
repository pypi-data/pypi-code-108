# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/1/26 4:20 PM
# LAST MODIFIED ON:
# AIM:
import os
import time
import sys
import re

from sentence_spliter_old.spliter import cut_to_sentences_en


def print_percent(current: int, max: int, header: str = ''):
    percent = float(current) / max * 100
    sys.stdout.write("\r{0}{1:.3g}%".format(header, percent))
    # sys.stdout.flush()


def print_time_cost(time_start: float, id: int, data_length: int, header: str = ''):
    time_lapse = time.time() - time_start
    average_lapse = time_lapse / float((id + 1))
    time_remain = average_lapse * (data_length - (id + 1))
    print_percent(id, data_length,
                  header='{0} total_datasize {1} [{2}|{3}]， avg_time_pre_batch {4:0.4f}s, time_remain {5}s - '.format(
                      header,
                      data_length,
                      id,
                      data_length,
                      average_lapse,
                      time.strftime("%H:%M:%S", time.gmtime(time_remain)))
                  )


novel_path = '/Users/Shared/cachi/sentence-spliter/测试小说/Bernard-Cornwell---The-Fort,-A-Novel-of-the-Revolutionary-War.txt'

with open(novel_path, 'r') as f:
    data = f.read().replace('\n', '')

data_length = len(data)

start_time = time.time()

out = cut_to_sentences_en(data)
#print_time_cost(start_time, i, data_length)
with open('split_sentences_result.txt', 'a') as f:
    f.write('\n\n'.join(v.strip() for v in out))
