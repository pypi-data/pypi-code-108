from libopensesame.py3compat import *

from libopensesame import debug
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin

class my_first_plugin(item):

    description = u'DESCRIPTION HERE PLEASE'

    def reset(self):

        self.var.my_line_edit_var = u'default value'
        self.var.my_checkbox_var = u'default value'

        debug.msg(u'My First Plugin Has Been Initialized')

    def prepare(self):

        item.prepare(self)

    def run(self):
        self.set_item_onset()


class qtmy_fist_plugin(my_first_plugin, qtautoplugin):

    def __init__(self, name, experiment, script=None):

        my_first_plugin.__init__(self, name, experiment, script)
        qtautoplugin.__init__(self, __file__)