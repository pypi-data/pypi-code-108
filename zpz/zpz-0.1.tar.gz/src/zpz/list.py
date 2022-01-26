import collections


def flatten(x):
    if x == []:
        return x
    if isinstance(x[0], list):
        return flatten(x[0]) + flatten(x[1:])
    return x[:1] + flatten(x[1:])


def ordered_dedupe(x):
    assert isinstance(x, list)
    return list(collections.OrderedDict.fromkeys(x))
