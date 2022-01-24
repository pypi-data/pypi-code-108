
from .trait_types import TraitBase
import traits.api as tr
from bmcs_utils.editors import InstanceEditor

class Instance(TraitBase, tr.Instance):
    editor_factory = InstanceEditor

    def get_sub_nodes(self):
        return []