# -*- coding: utf-8 -*-
from alphalogic_api3.objects import Root, Object
from alphalogic_api3.decorators import command
from alphalogic_api3 import init


class MyRoot(Root):

    def handle_get_available_children(self):
        return [
            (TreeChecker, 'TreeChecker')
        ]


def uint64_to_int64(i):
    _MAX = (1 << 63) - 1
    return -(i - _MAX) if i > _MAX else i


class TreeChecker(Object):

    @command(result_type=int)
    def get_root_id(self):
        return self.root().id

    @command(result_type=int)
    def get_child_num(self):
        return len(self.children())

    @command(result_type=int)
    def get_child_id(self, index=0):
        _id = -1
        if self.children():
            _id = self.children()[index].id
        return _id

    @command(result_type=int)
    def get_root_id(self):
        id = self.root().id
        return id

    def handle_get_available_children(self):
        return [
            (TreeChecker, 'TreeChecker')
        ]


if __name__ == '__main__':
    # python loop
    root = MyRoot()
    root.join()
