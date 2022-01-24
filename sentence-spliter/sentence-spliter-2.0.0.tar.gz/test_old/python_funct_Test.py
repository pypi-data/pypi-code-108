# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/13 4:55 PM
# LAST MODIFIED ON:
# AIM:

import time
import matplotlib.pyplot as plt


def run_single(sample_size):
    a = '(太阳当空照).(花儿对我笑)，"小鸟说早早"，"你为什么背上书包了,".　\
    我去上学校,天天不迟到，爱学习爱劳.' * sample_size
    a = list(a)
    start_t = time.time()
    # while a:
    #   a.pop()
    # a.pop(0)
    for v in a:
        c = 1 + 1
    end_t = time.time() - start_t
    return end_t, a


def test():
    time = []
    size = []
    for i in range(1000, 1000000, 1000):
        t, out = run_single(i)
        # if not check(options, sentence_list=out):
        #     raise Exception('分句错误')
        time.append(t)
        size.append(i)
        if i % 100 == 0:
            print(i)
            plt.figure()
            plt.plot(time)
            plt.savefig('perform')
            plt.close()


if __name__ == '__main__':
    test()
