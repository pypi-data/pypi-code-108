from collections.abc import MutableMapping, MutableSequence


def intersect(i1, i2):
    if isinstance(i1, MutableMapping):
        return intersect_map(i1,i2)
    elif isinstance(i1, MutableSequence):
        return intersect_seq(i1,i2)
    elif i1 == i2:
        return i1


def intersect_map(m1, m2, depth=0):
    intersection = {}
    for k in m1:
        if k in m2:
            c = intersect(m1[k], m2[k])
            if c:
                intersection[k] = c
    return intersection

def intersect_seq(s1, s2, depth=0):
    intersection = []
    for i in range(len(s1)):
        if i < len(s2):
            c = intersect(s1[i], s2[i])
            if c: intersection.append( c )
    return intersection

