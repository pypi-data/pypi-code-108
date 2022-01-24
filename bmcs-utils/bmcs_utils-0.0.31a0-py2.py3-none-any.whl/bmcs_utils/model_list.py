
from .model import Model
from .trait_types.list_type import List
import traits.api as tr
from .view import View

class ModelList(Model):

    items = List([])
    item_keys = tr.Property
    def _get_item_keys(self):
        return [item.name for item in self.items]
    item_dict = tr.Property
    def _get_item_dict(self):
        return {key : value for key, value in zip(self.item_keys, self.items)}

    def __getitem__(self, key):
        return self.item_dict[key]

    @tr.observe('items_items')
    def items_list_changed(self, event):
        if self.state_change_debug:
            print('LIST STATE CHANGED', event)
        self.state_changed = True

    tree = tr.Property
    def _get_tree(self):
        return self.item_keys

    def get_submodels(self):
        return self.items

