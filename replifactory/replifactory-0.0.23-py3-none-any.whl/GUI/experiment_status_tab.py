import ipywidgets as widgets
from IPython.core.display import clear_output
from ipywidgets import VBox


class ExperimentStatusTab:
    title = "Status"

    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.button = widgets.Button(description="show status", icon="fa-info-circle")
        self.output = widgets.Output()
        self.button.on_click(self.handle_button_action)
        self.widget = VBox([self.button, self.output])

    def handle_button_action(self, button):
        with self.output:
            clear_output()
            self.main_gui.experiment.status(increase_verbosity=True)
