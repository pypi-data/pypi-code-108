# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-10-25 18:00:46
@LastEditTime: 2021-10-28 15:06:22
@LastEditors: HuangJianYi
@Description: 
"""
import math
import redis
import mmh3


class BloomFilterHelper():
    """
    :description: 布隆过滤器（Bloom Filter）是 1970 年由布隆提出的。它实际上是一个很长的二进制向量和一系列随机映射函数。布隆过滤器可以用于检索一个元素是否在一个集合中。它的优点是空间效率和查询时间都比一般的算法要好的多，缺点是有一定的误识别率和删除困难。
    :return: 
    :last_editors: HuangJianYi
    """
    #内置100个随机种子
    SEEDS = [543, 460, 171, 876, 796, 607, 650, 81, 837, 545, 591, 946, 846, 521, 913, 636, 878, 735, 414, 372, 344, 324, 223, 180, 327, 891, 798, 933, 493, 293, 836, 10, 6, 544, 924, 849, 438, 41, 862, 648, 338, 465, 562, 693, 979, 52, 763, 103, 387, 374, 349, 94, 384, 680, 574, 480, 307, 580, 71, 535, 300, 53, 481, 519, 644, 219, 686, 236, 424, 326, 244, 212, 909, 202, 951, 56, 812, 901, 926, 250, 507, 739, 371, 63, 584, 154, 7, 284, 617, 332, 472, 140, 605, 262, 355, 526, 647, 923, 199, 518]

    def __init__(self, capacity=1000000000, error_rate=0.00000001, conn=None, key='bloom_filter',expire=0):
        """
        :description: 初始化
        :param capacity: 预先估计要去重的数量
        :param error_rate: 错误率
        :param conn: redis的连接客户端
        :param key: 键的名字前缀
        :param expire: 过期时间（单位秒）
        :return:
        :last_editors: HuangJianYi
        """
        self.m = math.ceil(capacity * math.log2(math.e) * math.log2(1 / error_rate))  #需要的总bit位数
        self.k = math.ceil(math.log1p(2) * self.m / capacity)  #需要最少的hash次数
        self.mem = math.ceil(self.m / 8 / 1024 / 1024)  #需要的多少M内存
        self.blocknum = math.ceil(self.mem / 512)  #需要多少个512M的内存块,value的第一个字符必须是ascii码，所有最多有256个内存块
        self.seeds = self.SEEDS[0:self.k]
        self.key = key
        self.N = 2**31 - 1
        self.redis = conn
        self.expire = expire

    def add(self, value):
        name = self.key + "_" + str(ord(value[0]) % self.blocknum)
        hashs = self.get_hashs(value)
        for hash in hashs:
            self.redis.setbit(name, hash, 1)
        if self.expire > 0:
            self.redis.expire(name, self.expire)


    def is_exist(self, value):
        name = self.key + "_" + str(ord(value[0]) % self.blocknum)
        hashs = self.get_hashs(value)
        exist = 1
        for hash in hashs:
            exist = exist & self.redis.getbit(name, hash)
        if exist == 1:
            return True
        else:
            return False

    def get_hashs(self, value):
        hashs = list()
        for seed in self.seeds:
            hash = mmh3.hash(value, seed)
            if hash >= 0:
                hashs.append(hash)
            else:
                hashs.append(self.N - hash)
        return hashs