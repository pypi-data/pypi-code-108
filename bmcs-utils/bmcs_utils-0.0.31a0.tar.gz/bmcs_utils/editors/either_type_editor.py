

import traits.api as tr
from .editors import EditorFactory
import ipywidgets as ipw

class EitherTypeEditor(EditorFactory):
    show_properties = tr.Bool(True)
    """Polymorphic instance editor.
    """
    def render(self):
        option_tuples = self.trait.options
        option_keys = [key for key, _ in option_tuples]
        key = getattr(self.model, self.name)
        self.drop_down = ipw.Dropdown(description=self.label, value=key,
                                 tooltip=self.tooltip, options=option_keys)
        self.drop_down.observe(self._selection_changed_from_dropdown,'value')
        self.model.observe(self._selection_changed_from_model,self.name)
        self.instance_pane = ipw.VBox(self._render_instance())

        if self.show_properties:
            return ipw.VBox([self.drop_down, self.instance_pane])
        else:
            return self.drop_down

    def _render_instance(self):
        app_window = self.controller.app_window
        submodel = getattr(self.model, self.name + '_')
        instance_controller = submodel.get_controller(app_window=app_window)
        model_editor = instance_controller.model_editor
        return [model_editor]

    def _selection_changed_from_dropdown(self, event):
        setattr(self.model, self.name, event['new'])
        self.instance_pane.children = self._render_instance()
        self.model.tree_changed = True

    def _selection_changed_from_model(self, event):
        option = getattr(self.model, self.name)
        self.drop_down.unobserve(self._selection_changed_from_dropdown,'value')
        self.drop_down.value = option
        self.drop_down.observe(self._selection_changed_from_dropdown,'value')
        self.instance_pane.children = self._render_instance()
        self.model.tree_changed = True
