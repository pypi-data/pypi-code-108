import ipywidgets as widgets
# from ipywidgets import VBox, Layout, HBox
# from replifactory.culture.morbidostat import MorbidostatCulture
# from replifactory.culture.turbidostat import TurbidostatCulture
# from replifactory.culture.endurance import EnduranceStressCulture
# from replifactory.culture.blank import BlankCulture
# from replifactory.experiment import Experiment
# import os
# import glob

from IPython.display import clear_output


class RunTab:
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.run_button = widgets.Button(description="RUN")
        self.stop_button = widgets.Button(description="STOP")
        if self.main_gui.experiment.is_running():
            self.run_button.disabled = True
        else:
            self.stop_button.disabled = True

        self.run_button.on_click(self.handle_run_button)
        self.widget = widgets.HBox([self.run_button, self.stop_button])

    def handle_run_button(self, b):
        with self.main_gui.status_bar.output:
            clear_output()
            self.main_gui.experiment.run()
        self.run_button.disabled = True
        self.stop_button.disabled = False

    def handle_stop_button(self, b):
        with self.main_gui.status_bar.output:
            clear_output()
            self.main_gui.experiment.stop()
        self.stop_button.disabled = True
        self.run_button.disabled = False




