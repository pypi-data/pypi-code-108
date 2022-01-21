# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/26 2:08 下午
# Copyright (C) 2021 The lesscode Team
from math import ceil


class Page:

    def __init__(self, total, current: int, page_size: int, records=None):
        self.records = records
        # 总记录数
        self.total = int(total)
        # 每页显示条数，默认 10
        self.page_size = int(page_size)
        # 当前页数
        self.current = int(current)
        # 总页数
        self.pages = ceil(int(self.total) / int(self.page_size))
        # 是否存在前一页
        self.hasPrevious: bool = int(self.current) > 1
        # 是否存在下一页
        self.hasNext: bool = int(self.current) < int(self.pages)

    @staticmethod
    def skip(page_num: int, page_size: int):
        """
        依据页码与条数 计算跳过索引
        :param page_num:
        :param page_size:
        :return:
        """
        return (int(page_num) - 1) * int(page_size)
