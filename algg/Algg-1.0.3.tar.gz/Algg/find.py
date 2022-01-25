# coding:utf-8

def linear_search(ls, target):
    """ 线性查找,时间复杂度为O(n) """
    for index, value in enumerate(ls):
        if value == target:
            return index
    return None


def binary_search(ls, target):
    """ 二分查找,时间复杂度为O(logn),要求列表是有序的 """
    left = 0
    right = len(ls) - 1
    while right >= left:  # 确保候选区有值
        mid = (right + left) // 2
        if ls[mid] == target:
            return mid
        elif ls[mid] > target:
            right = mid - 1
        else:
            # ls[mid] < target
            left = mid + 1
    return None
