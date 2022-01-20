# -*- coding: UTF-8 -*-
# @Time    : 2021/4/22
# @Author  : xiangyuejia@qq.com
# Apache License
# Copyright©2020-2021 xiangyuejia@qq.com All Rights Reserved
from cppbktree import BKTree

tree = BKTree( [ bytes( [ x ] ) for x in [0, 4, 5, 14] ] )
tree.add( bytes( [ 15 ] ) )
print( tree.find( 13, 1 ) )