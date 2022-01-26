"""set difference"""

from .equal import equal


def subtract(obj1, obj2):
    if type(obj1) == type(obj2):
        if isinstance(obj1, dict):
            res = dict()
            for k in obj1:
                if k in obj2:
                    tmp = subtract(obj1[k], obj2[k])
                    if tmp:
                        res[k] = tmp
                else:
                    res[k] = obj1[k]
            if len(res) > 0:
                return res
        elif isinstance(obj1, list) or isinstance(obj1, tuple):
            res = list()
            for v in obj1:
                found = False
                for i in range(len(obj2)):
                    if equal(v, obj2[i]):
                        found = True
                        break
                if not found:
                    res.append(v)
            if len(res) > 0:
                return res
        else:
            if obj1 == obj2:
                return None
            return obj1
    return None
