

import traits.api as tr
from .editors import EditorFactory
import ipywidgets as ipw

class EnumTypeEditor(EditorFactory):
    """Polymorphic instance editor.
    """
    def render(self):
        option_keys = self.trait.options
        key = getattr(self.model, self.name)
        drop_down = ipw.Dropdown(description=self.label, value=key,
                                 tooltip=self.tooltip, options=option_keys)
        drop_down.observe(self._selection_changed,'value')
        return drop_down

    def _selection_changed(self, event):
        setattr(self.model, self.name, event['new'])
