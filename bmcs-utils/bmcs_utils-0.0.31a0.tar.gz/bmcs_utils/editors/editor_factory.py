
import traits.api as tr

class EditorFactory(tr.HasTraits):
    name = tr.Str
    model = tr.WeakRef
    tooltip = tr.Str
    value = tr.Any
    trait = tr.Trait
    label = tr.Str
    disabled = tr.Bool(False)
    ui_pane = tr.WeakRef


