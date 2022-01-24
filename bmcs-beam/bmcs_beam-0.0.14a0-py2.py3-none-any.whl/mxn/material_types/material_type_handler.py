'''
Created on 29. 6. 2014

@author: Vancik
'''

from traits.api import \
    Instance, Button, Str, Trait

from traitsui.api import \
    View, Item, HGroup, Handler, spring, UIInfo

class MaterialTypeHandler(Handler):
    '''
    '''

    # The UIInfo object associated with the view:
    info = Instance(UIInfo)

    ok = Button('OK')
    delete = Button('OK')
    cancel = Button('Cancel')

    law_name = Str

    # The customization view:
    new_view = View(
        HGroup(
            spring,
            Item('law_name'),
            Item('law_type'),
            Item('ok', show_label=False),
            Item('cancel', show_label=False),
        ),
        kind='live'
    )

    del_view = View(
        HGroup(
            spring,
            Item(name='', label='Really delete?'),
            Item('delete', show_label=False),
            Item('cancel', show_label=False),
        ),
        kind='popup'
    )

    # Event handlers:
    def object_new_law_changed (self, info):
        if info.initialized:
            self.info = info
            laws = info.object.possible_laws
            self.add_trait('law_type', Trait(list(laws.values())[0], laws))
            self._ui = self.edit_traits(parent=info.new_law.control, view='new_view')

    def object_del_law_changed (self, info):
        if info.initialized:
            self.info = info
            self._ui = self.edit_traits(parent=info.del_law.control, view='del_view')

    def _ok_fired (self):
        object = self.info.object
        if self.law_name == '':
            print('Please enter law name!')
        elif object.mtrl_laws.get(self.law_name, None):
            print('Law name already occupied!')
        else:
            object.mtrl_laws[self.law_name] = self.law_type_()
            self._ui.dispose()
            self.info.ui.parent.updated = True

    def _delete_fired (self):
        object = self.info.object
        del object.mtrl_laws[object.chosen_law]
        self._ui.dispose()
        self.info.ui.parent.updated = True

    def _cancel_fired (self):
        self._ui.dispose()
