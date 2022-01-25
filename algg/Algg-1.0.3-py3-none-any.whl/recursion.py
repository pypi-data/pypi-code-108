# coding:utf-8

def get_fib(n):
    """ 求出长度为 num 的 fib 数列 """
    fib_list = []
    for i in range(n):
        if len(fib_list) < 2:
            fib_list.append(1)
            continue
        fib_list.append(fib_list[-1] + fib_list[-2])
    return fib_list


def fib_recur(n):
    """ 常规方式 求出 fib 数列的第 n 个数 """
    # 递归,时间复杂度为O(2^n)
    if n <= 1:
        return n
    else:
        return fib_recur(n - 1) + fib_recur(n - 2)


def fib_recur_list(n):
    """ 求出 fib 数列的第 n 个数 """
    fib_ls = []
    for i in range(n):
        if len(fib_ls) < 2:
            fib_ls.append(1)
            continue
        fib_ls.append(fib_ls[-1] + fib_ls[-2])
    # print(fib_ls)
    return fib_ls[n - 1]


def fib_loop(n):
    """ 循环方式 求出 fib 数列的第 n 个数 """
    if n <= 1:
        return n
    # 递推,时间复杂度为O(n)
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a


def fib_gen(n):
    """ 生成器函数 - 斐波那契 """
    a, b, counter = 0, 1, 0
    while True:
        if counter > n:
            return
        yield a
        a, b = b, a + b
        counter += 1


def hanoi(n, a, b, c):
    """ 汉诺塔简单实现 """
    if n > 0:
        hanoi(n - 1, a, c, b)
        print('moving from %s to %s' % (a, c))
        hanoi(n - 1, b, a, c)
