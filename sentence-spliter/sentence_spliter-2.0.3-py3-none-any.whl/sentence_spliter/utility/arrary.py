# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/26 4:48 PM
# LAST MODIFIED ON:
# AIM:

from typing import List


def flatten(array: List) -> List:
    out = []
    for v in array:
        if type(v) == list:
            out.extend(flatten(v))
        else:
            out.append(v)
    return out
