"""set intersection"""

from .equal import equal


def intersection(obj1, obj2):
    """intersection operation for 2 JSON objects.
    :param obj1: first json object
    :param obj2: second json object
    :return: a json object that reflects "obj1 & ojb2"
    """
    if type(obj1) == type(obj2):
        if isinstance(obj1, dict):
            res = dict()
            for k in obj1:
                if k in obj2:
                    tmp = intersection(obj1[k], obj2[k])
                    if tmp:
                        res[k] = tmp
            if len(res) > 0:
                return res
        elif isinstance(obj1, list) or isinstance(obj1, tuple):
            mark = [0 for _ in range(len(obj2))]
            res = list()
            for v in obj1:
                for i in range(len(mark)):
                    if mark[i] == 0 and equal(v, obj2[i]):
                        mark[i] = 1
                        res.append(v)
            if len(res) > 0:
                return res
        elif obj1 == obj2:
            return obj1
    return None

