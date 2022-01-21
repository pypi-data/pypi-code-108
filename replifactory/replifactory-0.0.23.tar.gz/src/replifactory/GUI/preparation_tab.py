import ipywidgets as widgets
from IPython.display import clear_output, display
from ipywidgets import VBox, HBox, Layout
import time
from replifactory.GUI.device_control_widgets import StirrerWidgets
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import numpy as np
import os
import glob


class PreparationTab:
    def __init__(self,main_gui):
        self.main_gui = main_gui
        self.device = self.main_gui.experiment.device
        self.add_1ml = widgets.Button(description="1. Add 1ml to all vials")
        self.current_volumes = HBox([widgets.IntSlider(value=1, min=0, max=15, orientation="vertical") for v in range(1,8)])
        self.fill_all = widgets.Button(description="2. fill all vials")
        self.vacuum_all = widgets.Button(description="3. vacuum all vials")
        self.output = widgets.Output()
        self.add_1ml.on_click(self.handle_add_1ml)
        self.fill_all.on_click(self.handle_fill_all)
        self.vacuum_all.on_click(self.handle_vacuum_all)
        self.widget = VBox([self.add_1ml, self.current_volumes, self.fill_all, self.vacuum_all, self.output])

    def handle_add_1ml(self,button):
        for v in range(1,8):
            volume = 1
            with self.output:
                clear_output()
                print("Pumping %.1f mL to vial %d" % (volume,v))
            self.device.pump_to(vial=v, pump1=volume)

    def handle_fill_all(self, button):
        for v in range(1, 8):
            volume = 15 - self.current_volumes.children[v].value
            with self.output:
                clear_output()
                print("Pumping %.1f mL to vial %d" % (volume, v))
            self.device.pump_to(vial=v, pump1=volume)

    def handle_vacuum_all(self,button):
        for v in range(1, 8):
            volume = 5
            with self.output:
                clear_output()
                print("Pumping %.1f mL to vial %d" % (volume, v))
            self.device.pump_to(vial=v, pump4=volume)
