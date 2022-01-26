# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Created: 2022/1/9
@Desc: 
"""


def remove(lst, item, raise_error=False):
    """
    移除元素
    :param lst:
    :param item: 被移除的元素
    :param raise_error: 是否抛出异常
    :return:
    """
    try:
        lst.remove(item)
    except ValueError:
        if raise_error:
            raise
    return lst


def remove_all(lst, *items, raise_error=False):
    """
    移除所有指定元素
    :param lst:
    :param items: 被移除的元素
    :param raise_error: 是否抛出异常
    :return:
    """
    for arg in items:
        if arg in lst:
            lst.remove(arg, raise_error)
    return lst


def append(lst, item, dup=True):
    """
    追加元素
    :param lst:
    :param item: 元素
    :param dup: 是否可重复
    :return:
    """
    if item in lst and not dup:
        return lst
    lst.append(item)
    return lst


def extend(lst, *items, dup=True):
    """
    扩展列表
    :param lst:
    :param items:
    :param dup:
    :return:
    """
    for item in items:
        lst.append(item, dup)
    return lst


def prepend(lst, *items, dup=True):
    """在列表头部添加元素"""
    for item in items:
        if item in lst and not dup:
            lst.remove(item)
            lst.insert(0, item)
            return lst
        lst.insert(0, item)
    return lst
