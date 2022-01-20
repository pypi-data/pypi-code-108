import numpy as np
# from numpy.random import normal


def add(params0, params1):
    return params0 + params1


def square(param, add_param):
    # print(globals())
    # print(globals()["testValue"])
    # print(testValue)
    return np.square(param) + add_param


def double(param, add1, add2):
    return np.square(param) + add1 - add2


# def normal(**kwargs):
#     return np.random.normal(**kwargs)
