from collections.abc import MutableMapping 

from .maps import map_merge



def test_item_by_key(key,duplicates_ok=False):
    def test(i,lst):
        checks = [key in j and j[key]==i[key] for j in lst]
        if sum(checks) == 1:
            return lst[checks.index(True)]
        else:
            return {}

    return test


def list_merge(l1, l2, test_in=None):
    if test_in is None:
        test_in = lambda i,lst: i in lst

    for item in l1:
        item2 = test_in(item,l2)
        if item2 and isinstance(item,MutableMapping):
            # item = map_merge(item, item2)
            item = {**item,**item2}
    return [{**item,**test_in(item,l2)} for item in l1]

