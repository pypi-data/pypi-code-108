#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : result
# @Time         : 2021/2/18 6:16 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.zk_utils import zk_cfg
from meutils.request_utils import request


def get_ac(docid, parser=lambda x: x.get('item', {})):
    return request(f"{zk_cfg.ac_url}/{docid}", parser=parser)


def get_acs(docids, max_workers=10, parser=lambda x: x.get('item', {}).get('title')):
    func = functools.partial(get_ac, parser=parser)
    return docids | xThreadPoolExecutor(func, max_workers) | xlist


def get_simbert_vectors(titles='bert向量化', max_workers=1, is_lite='0'):
    """
    适合小批量请求
    :param titles:
    :param max_workers:
    :param is_lite:
    :return:
    """
    if isinstance(titles, str):
        titles = [titles]

    max_workers = min(len(titles), max_workers)
    titles_list = np.array_split(titles, len(titles) // 64 + 1)  # list
    request_func = lambda titles: request(f"{zk_cfg.simbert_url}",
                                          json={"texts": list(titles), "is_lite": is_lite}).get('vectors')

    vectors_list = titles_list | xThreadPoolExecutor(request_func, max_workers)

    return np.row_stack(vectors_list)


if __name__ == '__main__':
    print(get_acs(['fengxing_144094389']))

    # print(get_simbert_vectors('bert向量化', is_lite='1').shape)
