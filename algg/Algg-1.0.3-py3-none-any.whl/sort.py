# coding:utf-8

def bubble_sort(ls):
    """ 冒泡，时间复杂度为O(n^2) """
    for i in range(len(ls) - 1):  # 第i趟,从0开始,只剩一个数时不需要最后一趟
        exchange = False
        for j in range(len(ls) - i - 1):  # j:无序区的索引指针,指针顾头不顾尾所以-1
            if ls[j] > ls[j + 1]:
                ls[j], ls[j + 1] = ls[j + 1], ls[j]
                exchange = True
        if not exchange:
            return
        # print(ls)


def select_sort(ls):
    """ 选择排序，时间复杂度O(n^2) """
    for i in range(len(ls) - 1):  # 第i趟
        # 无序区最小值的索引位置,默认i
        min_loc = i
        # 遍历无序区
        for j in range(i, len(ls)):
            if ls[j] < ls[min_loc]:
                min_loc = j
        # 找到无序区最小数,与无序区第一个数交换
        ls[i], ls[min_loc] = ls[min_loc], ls[i]


def insert_sort(ls):
    """ 插入排序，时间复杂度O(n^2) """
    for i in range(1, len(ls)):  # i表示摸到的牌(无序区)的下标
        j = i - 1  # j表示手里的牌(有序区)的下标
        # 1.j>i,将j右挪,将i插到j前面 || 2.j<i,直接插到j后面
        # 重要！要将摸到的牌存变量
        tmp = ls[i]
        while ls[j] > tmp and j >= 0:
            # 右挪
            ls[j + 1] = ls[j]
            j -= 1
        ls[j + 1] = tmp


def quick_sort(ls, left, right):
    """ 快速排序，时间复杂度O(nlogn) """
    if left < right:  # 至少有两个元素
        mid = partition(ls, left, right)
        quick_sort(ls, left, mid - 1)
        quick_sort(ls, mid + 1, right)


def partition(ls, left, right):
    tmp = ls[left]
    while left < right:
        # 取列表的第一个元素tmp,使tmp归位->左边有空->从右边开始找
        while left < right and ls[right] >= tmp:
            # 找比tmp小的，当右边的元素<tmp时跳出循环，不然一直向左找
            right -= 1
        # 找到了比tmp小的right，将它写到空位上(left)
        ls[left] = ls[right]
        # print('---moving from right to left---:{}'.format(ls))
        # 右边有空->从左边找
        while left < right and ls[left] <= tmp:
            # 找比tmp大的元素...
            left += 1
        # 找到了比tmp大的left，将它写到空位上(right)
        ls[right] = ls[left]
        # print('---moving from left to right---:{}'.format(ls))
    # 当left=right时跳出循环,可写ls[left]/ls[right]
    ls[left] = tmp
    return left
