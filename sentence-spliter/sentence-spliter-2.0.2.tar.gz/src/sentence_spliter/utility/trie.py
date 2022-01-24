# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/11/23 10:26 AM
# LAST MODIFIED ON:
# AIM: 字典树

from typing import List, Optional


class Render:
    def __init__(self):
        self.render_list = []

    @staticmethod
    def child_mid() -> str:
        return '├──'

    @staticmethod
    def child_end() -> str:
        return '└──'

    @staticmethod
    def parent() -> str:
        return '│'


class Trie:
    def __init__(self, key: object):
        self.value = key
        self.children = dict()
        self.path = str(self.value)

    def __str__(self):
        return str(self.value)

    def __getitem__(self, item: str):
        return self.children[item]

    def __contains__(self, item: str):
        return item in self.children

    def __add_tok(self, tok: str):
        if tok not in self.children:
            child = Trie(tok)
            child.path = f'{self.path} {str(child)}'
            self.children[tok] = child
            return child
        return self.children[tok]

    def add_phrase(self, phrase: List[str]):
        tree = self
        for value in phrase:
            tree = tree.__add_tok(value)
        tree.__add_tok('<end>')
        return self

    def show(self, header: List = [], bool_last: bool = False):
        front = '\t'.join(header)
        print(f'{front}{self.value}')

        items_list = list(self.children.items())
        if not items_list:
            return
        elif header:
            if bool_last:
                header[-1] = ''
            else:
                header[-1] = Render.parent()
        for key, child in items_list[0:-1]:
            child.show(header + [Render.child_mid()])
        key, child = items_list[-1]
        child.show(header + [Render.child_end()], True)

    def next(self, tok: str):
        return self.children.get(tok, None)

    def is_end_node(self, tok:str):
        if tok not in self and '<end>' in self:
            return True
        return False