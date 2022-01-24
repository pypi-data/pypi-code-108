

import traits.api as tr
from .editors import EditorFactory
from bmcs_utils.i_model import IModel

class InstanceEditor(EditorFactory):

    value = tr.Instance(IModel)

    def render(self):
        app_window = self.controller.app_window
        instance_controller = self.value.get_controller(app_window=app_window)
        model_editor = instance_controller.model_editor
        return model_editor
