# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/6/8 4:36 PM
# LAST MODIFIED ON:
# AIM: 测试模型速度

from sentence_spliter_old import Spliter
import matplotlib.pyplot as plt
import time
from utility.time_it import time_measure


def check(options, sentence_list) -> bool:
    for sentence in sentence_list:
        if not (options['min_length'] <= len(sentence) <= options['max_length']):
            return False
    else:
        return True


def run_single(options, sample_size=1):
    sentence = '(太阳当空照).(花儿对我笑)，"小鸟说早早"，"你为什么背上书包了,".　\
    我去上学校,天天不迟到，爱学习爱劳.' * sample_size
    spliter = Spliter(options)
    start_t = time.time()
    cut_sentences = spliter.cut_to_sentences(sentence)
    end_t = time.time() - start_t
    return end_t, cut_sentences


def test(options):
    time = []
    size = []
    for i in range(1000, 1000000, 1000):
        t, out = run_single(options, i)
        if not check(options, sentence_list=out):
            raise Exception('分句错误')
        time.append(t)
        size.append(i)
        if i % 100 == 0:
            print(i)
            plt.figure()
            plt.plot(time)
            plt.savefig('perform')
            plt.close()


if __name__ == '__main__':
    options = {
        'language': 'zh',  # 'zh'中文 'en' 英文
        'long_short_sent_handle': 'y',  # 'y'自然切分，不处理长短句；'n'处理长短句
        'max_length': 5,  # 最长句子，默认值150
        'min_length': 4,  # 最短句子，默认值15
        'hard_max_length': 5,  # 强制截断，默认值300
        'remove_blank': True
    }
    test(options)
    #print(run_single(options, 15000))
