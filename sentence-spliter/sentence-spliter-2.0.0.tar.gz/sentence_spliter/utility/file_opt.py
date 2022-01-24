# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/16 9:56 AM
# LAST MODIFIED ON:
# AIM:

def read_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()
