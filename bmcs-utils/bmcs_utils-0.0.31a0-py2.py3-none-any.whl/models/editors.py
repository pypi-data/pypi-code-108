import traits.api as tr
import ipywidgets as ipw


class EditorFactory(tr.HasTraits):
    name = tr.Str
    model = tr.WeakRef
    tooltip = tr.Str
    value = tr.Any
    trait = tr.Trait
    label = tr.Str


class FloatEditor(EditorFactory):
    def render(self):
        print('tooltip', self.name, self.tooltip)
        return ipw.FloatText(description=self.label, value=self.value, tooltip=self.tooltip)


class IntEditor(EditorFactory):
    def render(self):
        print('tooltip', self.name, self.tooltip)
        return ipw.IntText(description=self.label, value=self.value, tooltip=self.tooltip)


class BoolEditor(EditorFactory):
    def render(self):
        return ipw.Checkbox(description=self.label, value=self.value, tooltip=self.tooltip)


class FloatRangeEditor(EditorFactory):
    low = tr.Float
    high = tr.Float
    low_name = tr.Str
    high_name = tr.Str
    n_steps = tr.Int(20)

    def render(self):
        if self.low_name:
            self.low = getattr(self.model,self.low_name)
        if self.high_name:
            self.high = getattr(self.model,self.high_name)
        step = (self.high - self.low) / self.n_steps
        return ipw.FloatSlider(
            value=self.value,
            min=self.low,
            max=self.high,
            step=step,
            tooltip=self.tooltip,
            continuous_update=False,
            description=r'\(%s\)' % self.label
        )


class ProgressEditor(EditorFactory):
    """
    Progress bar running between 0 and 1 by default
    """
    min = tr.Float(0)
    max = tr.Float(1)
    min_name = tr.Str
    max_name = tr.Str

    def render(self):
        if self.min_name:
            self.min = getattr(self.model,self.min_name)
        if self.max_name:
            self.max = getattr(self.model,self.max_name)
        progress = ipw.FloatProgress(
            min=self.min, max=self.max,
            value = self.value,
            tooltip=self.tooltip
        )
        def notify_change(value):
            self.value = value
            progress.value = value
        self.trait.trait_type.add_notify(notify_change)
        return progress

class ButtonEditor(EditorFactory):
    def render(self):
        button = ipw.Button(
            description=self.label,
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip=self.tooltip,
            icon='check' # (FontAwesome names without the `fa-` prefix)
        )
        def button_clicked(change):
            setattr(self.model, self.name, True)
        button.on_click(button_clicked)
        return button