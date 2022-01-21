# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2019\10\8 0008 23:45
# @Author: "John"


def get_sorted_un_duplicated_list(li):
    """
        将给定的 list 进行去重，并按照原来的顺序返回
    :param li:
    :return:
    """
    if len(li):
        rest = []
        temp_set = set()
        for item in li:
            temp_set_size_bf = len(temp_set)
            temp_set.add(item)
            temp_set_size_aft = len(temp_set)
            # set size 有变化，说明该 item 不在 set 中；
            if temp_set_size_aft > temp_set_size_bf:
                rest.append(item)
            else:
                # 打印重复的那个
                # print(item)
                pass
        return rest
