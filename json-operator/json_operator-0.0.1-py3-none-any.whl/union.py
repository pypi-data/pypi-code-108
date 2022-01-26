"""set union"""

from .equal import equal


def union(obj1, obj2):
    if type(obj1) == type(obj2):
        if isinstance(obj1, dict):
            res = dict()
            both = set()
            for k in obj1:
                if k in obj2:
                    tmp = union(obj1[k], obj2[k])
                    if tmp:
                        res[k] = tmp
                    both.add(k)
            for k in obj1:
                if k not in both:
                    res[k] = obj1[k]
            for k in obj2:
                if k not in both:
                    res[k] = obj2[k]
            return res
        elif isinstance(obj1, list) or isinstance(obj1, tuple):
            mark = [0 for _ in range(len(obj2))]
            res = list()
            for v in obj1:
                for i in range(len(mark)):
                    if mark[i] == 0 and equal(v, obj2[i]):
                        mark[i] = 1
            res.extend(obj1)
            for i in range(len(mark)):
                if not mark[i]:
                    res.append(obj2[i])
            return res
        elif obj1 == obj2:
            return obj1
    return None

