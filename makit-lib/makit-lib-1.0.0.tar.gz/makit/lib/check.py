#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""
import re


def check(o, **kwargs):
    r = True
    for k, v in kwargs.items():
        pattern = re.compile(r'(?P<attr>[a-zA-Z][a-zA-Z0-9]*_?[a-zA-Z0-9]+)(__(?P<not>not_)?(?P<method>\w+))?')
        d = pattern.match(k).groupdict()
        attr = d.get('attr')
        _not = d.get('not') is not None
        method = d.get('method')
        if isinstance(o, dict):
            value = o.get(attr)
        else:
            value = getattr(o, attr, None)
        if not method:
            result = value == v
        elif method == 'in':
            result = value in v
        else:
            if method.startswith('i') and isinstance(value, str):
                value = value.lower()
                v = v.lower()
                method = method[1:]
            if method == 'contains':
                result = v in value
            elif method == 'startswith':
                result = value.startswith(v)
            elif method == 'endswith':
                result = value.endswith(v)
            elif method == 'matches':
                result = re.match(re.compile(v), value) is not None
            elif method == 'none':
                result = value is None and v
            elif method == 'lt':
                result = value < v
            elif method == 'gt':
                result = value > v
            elif method == 'le':
                result = value <= v
            elif method == 'ge':
                result = value >= v
            else:
                raise RuntimeError(f'Do not support method: {method}')
        if _not:
            result = not result
        r = r and result
    return r


def diff_list(lst, other):
    """
    Differ two list.
    :param lst:
    :param other:
    :return:（missing_set, extra_set）
    """
    missing, extra = set(), set()

    def _diff(this, another):
        if not this:
            missing.union(another)
        elif not another:
            extra.union(this)
        else:
            this_pop = this.pop(0)
            another_pop = another.pop(0)
            if this_pop != another_pop:
                if this_pop not in other and another_pop in lst:
                    extra.add(this_pop)
                    another.insert(0, another_pop)
                elif another_pop not in lst and this_pop in other:
                    missing.add(another_pop)
                    this.insert(0, this_pop)
                elif this_pop not in other and another_pop not in lst:
                    extra.add(this_pop)
                    missing.add(another_pop)
            _diff(this, another)

    _diff(lst, other)
    return missing, extra
