# -*- coding: utf-8 -*-
from functools import partial

from alphalogic_api3.objects import Root, Object
from alphalogic_api3.objects import ParameterString

'''
There are handlers available:
1) handler will be executed after parameter was changed

2) handle_prepare_for_work
Handler is executed before work of object

3) handle_defaults_loaded
Handler for configure Object after creation.

4) handle_before_remove_device
Handler is executed before object node was deleted

5) handle_get_available_children
Return possible objects for creation

'''


class Controller(Object):

    def __init__(self, type_device, id_device, **kwargs):
        super(Controller, self).__init__(type_device, id_device, **kwargs)
        if 'param' in kwargs:
            kwargs['param']()
        else:
            self.root().check_list.val += 'no param in init (loaded from configuration)'

    def handle_defaults_loaded(self, **kwargs):
        if 'param' in kwargs and 'number' in kwargs:
            self.root().check_list.val += ';handle_defaults_loaded'

    def handle_prepare_for_work(self):
        self.root().check_list.val += ';handle_prepare_for_work'

    def handle_before_remove_device(self):
        self.root().check_list.val += ';handle_before_remove_device'


class MyRoot(Root):

    check_list = ParameterString()

    def handle_get_available_children(self):

        def handler():
            self.check_list.val += 'param_in_init'

        r = []
        f = partial(Controller, number=1, param=handler)
        f.cls = Controller
        r.append((f, 'Controller'))

        return r


if __name__ == '__main__':
    # python loop
    root = MyRoot()
    root.join()
