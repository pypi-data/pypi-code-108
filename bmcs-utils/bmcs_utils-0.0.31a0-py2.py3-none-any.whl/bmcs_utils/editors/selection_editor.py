

import traits.api as tr
from .editors import EditorFactory
import ipywidgets as ipw

class SelectionEditor(EditorFactory):
    options_trait = tr.Str
    def render(self):
        options = getattr(self.model, self.options_trait)
        option_tuples = [(key, item) for key, item in options.items()]
        return ipw.Dropdown(description=self.label, value=option_tuples[0][1],
                            tooltip=self.tooltip, options=option_tuples)
