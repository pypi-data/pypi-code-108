import traits.api as tr
import ipywidgets as ipw
import numpy as np
from .editor_factory import EditorFactory

# This style insures that the widget label doesn't take additional white space
style = {'description_width': 'initial'}


class FloatRangeSliderEditor(EditorFactory):
    low = tr.Float
    high = tr.Float
    low_name = tr.Str
    high_name = tr.Str
    n_steps = tr.Int(20)
    n_steps_name = tr.Str
    continuous_update = tr.Bool(False)

    def render(self):
        if self.low_name:
            self.low = getattr(self.model, str(self.low_name))
        if self.high_name:
            self.high = getattr(self.model, str(self.high_name))
        if self.n_steps_name:
            self.n_steps = getattr(self.model, str(self.n_steps_name))

        return ipw.FloatRangeSlider(
            value=self.value,
            min=self.low,
            max=self.high,
            step=(self.high - self.low) / self.n_steps,
            tooltip=self.tooltip,
            continuous_update=self.continuous_update,
            description=self.label,
            disabled=self.disabled,
            readout=self.readout,
            style=style
        )