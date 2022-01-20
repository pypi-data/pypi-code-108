# -*- coding: UTF-8 -*-
# @Time    : 2021/4/7
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
# export PATH=/root/xbktree/:$PATH
# export PATH=/root/xbktree/:$PATH
import Levenshtein
import time
import pandas as pd
from tqdm import tqdm
from xbktree.bktree import BkTree, ftree
from typing import List, Any


def save_excel(data: List[Any], file: str, index=False, header=False) -> None:
    df = pd.DataFrame(data)
    df.to_excel(file, index=index, header=header)


def read_lines(file: str) -> List[Any]:
    with open(file, 'r', encoding='utf8') as fin:
        data = [d.strip() for d in fin.readlines()]
    return data


def write_lines(data: List[Any], file: str) -> None:
    with open(file, 'w', encoding='utf8') as fout:
        for d in data:
            print(d, file=fout)


def read_data(file='dataset/icd10/bktree_test_data_1.txt'):
    data = read_lines(file)
    return data


def make_cup(data: List[str]) -> List[dict]:
    data_cup = {}
    for d in data:
        key = len(d)
        if key not in data_cup:
            data_cup[key] = []
        data_cup[key].append(d)
    return data_cup


def rank_copy(data: List[str]) -> List[str]:
    return data


def rank_length_descending(base: int=0):
    def rank_length(data: List[str]):
        data_cup = make_cup(data)
        ranker = []
        for i in data_cup.keys():
            ranker.append([i, abs(k-base)])
        ranker.sort(key=lambda x: x[1])
        new_data = []
        for i, _ in ranker:
            new_data += data_cup[i]
        return new_data
    return rank_length


def make_test(
        node_file,
        test_file,
        distance=Levenshtein.distance,
        step=7,
        topk=100,
        rank_mode=rank_copy,
):
    node_data = rank_mode(read_data(file=node_file))
    test_data = read_data(file=test_file)
    test_data_cup = make_cup(test_data)
    tree = BkTree(node_data, distance)
    tree.builder(node_data)

    cup_index = sorted(list(test_data_cup.keys()))
    size_test_data = len(test_data)
    total_time = 0
    out_head = []
    out_data = []
    for i in cup_index:
        t0 = time.time()
        count = 0
        size_data_cup = len(test_data_cup[i])
        for q in test_data_cup[i][:topk]:
            count += 1
            ftree(tree, q, step)
        t1 = time.time()
        tavg = (t1 - t0) / count
        total_time += (size_data_cup / size_test_data) * tavg
        print('cup%d(%d/%d):\t\t%.4fs' % (i, count, size_data_cup, tavg))
        out_head.append('cup%d(%d/%d)' % (i, count, size_data_cup))
        out_data.append('%.4fs'%tavg)
    print('total:\t\t%.4fs' % total_time)
    out_head.append('total')
    out_data.append('%.4fs' % total_time)
    return out_head, out_data


if __name__ == '__main__':
    out_data = []
    for k in range(1,15):
        print('\n####')
        print('k is:', k)
        h, d = make_test(
            'dataset/icd10/all_tree_nodes.txt',
            'dataset/icd10/bktree_test_data_1.txt',
            step=k,
            topk=20,
            rank_mode=rank_copy,
        )
        if not out_data:
            out_data.append(['k'] + h)
        out_data.append([k] + d)
    save_excel(out_data, 'result_ori.xlsx')

    out_data = []
    for k in range(1,15):
        print('\n####')
        print('k is:', k)
        h, d = make_test(
            'dataset/icd10/all_tree_nodes.txt',
            'dataset/icd10/bktree_test_data_1.txt',
            step=k,
            topk=20,
            rank_mode=rank_length_descending(base=0),
        )
        if not out_data:
            out_data.append(['k'] + h)
        out_data.append([k] + d)
    save_excel(out_data, 'result_base0.xlsx')

    out_data = []
    for k in range(1,15):
        print('\n####')
        print('k is:', k)
        h, d = make_test(
            'dataset/icd10/all_tree_nodes.txt',
            'dataset/icd10/bktree_test_data_1.txt',
            step=k,
            topk=20,
            rank_mode=rank_length_descending(base=3),
        )
        if not out_data:
            out_data.append(['k'] + h)
        out_data.append([k] + d)
    save_excel(out_data, 'result_base3.xlsx')

    out_data = []
    for k in range(1, 15):
        print('\n####')
        print('k is:', k)
        h, d = make_test(
            'dataset/icd10/all_tree_nodes.txt',
            'dataset/icd10/bktree_test_data_5.txt',
            step=k,
            topk=20,
            rank_mode=rank_length_descending(base=5),
        )
        if not out_data:
            out_data.append(['k'] + h)
        out_data.append([k] + d)
    save_excel(out_data, 'result_base5.xlsx')

    out_data = []
    for k in range(1, 15):
        print('\n####')
        print('k is:', k)
        h, d = make_test(
            'dataset/icd10/all_tree_nodes.txt',
            'dataset/icd10/bktree_test_data_1.txt',
            step=k,
            topk=20,
            rank_mode=rank_length_descending(base=7),
        )
        if not out_data:
            out_data.append(['k'] + h)
        out_data.append([k] + d)
    save_excel(out_data, 'result_base7.xlsx')

    # for k in range(1,15):
    #     print('\n####')
    #     print('k is:', k)
    #     make_test(
    #         'dataset/icd10/all_tree_nodes.txt',
    #         'dataset/icd10/bktree_test_data_2.txt',
    #         step=k,
    #         topk=20,
    #     )
    # for k in range(1,15):
    #     print('\n####')
    #     print('k is:', k)
    #     make_test(
    #         'dataset/drug/all_tree_nodes.txt',
    #         'dataset/drug/bktree_test_data_1.txt',
    #         step=k,
    #         topk=20,
    #     )
# data = read_data(file='dataset/icd10/bktree_test_data_1.txt')
# tree = BkTree(data, Levenshtein.distance)
# tree.builder(data)
# x = ftree(tree, '气管炎', 7)
# print("x:", len(x), x)
#
# data = read_data(file='dataset/icd10/bktree_test_data_2.txt')
# tree = BkTree(data, Levenshtein.distance)
# tree.builder(data)
# x = ftree(tree, '气管炎', 7)
# print("x:", len(x), x)
#
# data = read_data(file='dataset/icd10/bktree_test_data_3.txt')
# tree = BkTree(data, Levenshtein.distance)
# tree.builder(data)
# x = ftree(tree, '气管炎', 7)
# print("x:", len(x), x)
#
# data = read_data(file='dataset/icd10/all_tree_nodes.txt')
# tree = BkTree(data, Levenshtein.distance)
# tree.builder(data)
# x = ftree(tree, '气管炎', 7)
# print("x:", len(x), x)