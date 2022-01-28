from collections import namedtuple, deque
from collections.abc import MutableMapping 


def get_nest(data, *args):
    """https://stackoverflow.com/questions/10399614/accessing-value-inside-nested-dictionaries"""
    if args and data:
        element  = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nest(value, *args[1:])

def compose(elements, tree, key=None, _built=False, node='ElemSpace'):
    """Apply function composition over a computational graph."""
    if key is None: 
        key = list(tree[node].keys())[0]
        tree = list(tree[node].values())[0]

    if node in tree and (not _built): # build grandchild elements
        tree[node] = {
            hkey: compose( elements, tree[node][hkey], key=hkey) 
            for hkey in [eli for eli in tree[node]] }

        return compose(elements, tree, key, True) # build child element
    else: return elements[key](**tree)

def build(elements, params, key=None, _built=False, tree='el'):
    if key is None: 
        key = list(params[tree].keys())[0]
        params = list(params[tree].values())[0]

    if tree in params and (not _built): # build grandchild elements
        params[tree] = {
            hkey: build( elements, params[tree][hkey], key=hkey) 
            for hkey in [eli for eli in params[tree]] }

        return build(elements, params, key, True) # build child element

    else: return elements[key](**params)


def map_merge(d1, d2):
    """
    Update two dicts of dicts recursively, 
    if either mapping has leaves that are non-dicts, 
    the second's leaf overwrites the first's.
    """
    for k, v in d1.items():
        if k in d2:
            if all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                d2[k] = map_merge(v, d2[k])
    d3 = d1.copy()
    d3.update(d2)
    return d3

def dict_depth(d:dict)->int:
    queue = deque([(id(d), d, 1)])
    memo = set()
    while queue:
        id_, o, level = queue.popleft()
        if id_ in memo:
            continue
        memo.add(id_)
        if isinstance(o, dict):
            queue += ((id(v), v, level + 1) for v in o.values())
    return level
