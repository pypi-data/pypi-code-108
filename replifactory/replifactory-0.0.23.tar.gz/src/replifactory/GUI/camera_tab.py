import ipywidgets as widgets
from ipywidgets import VBox, HBox
import time
import os


class CameraTab:
    def __init__(self):
        self.title = "Camera"
        self.button = widgets.Button(description="photo", icon="camera")
        output = widgets.Output()
        img_widget = widgets.Image(format='png', width=600, height=400)
        self.vflip = widgets.Checkbox(value=False, description="vertical flip")
        self.hflip = widgets.Checkbox(value=False, description="horizontal flip")

        def on_button_clicked(b):
            self.button.disabled = True
            self.button.description = "busy"
            additional_args = ""
            if self.vflip.value:
                additional_args += " --vflip"
            if self.hflip.value:
                additional_args += " --hflip"

            res = os.system("raspistill -o photo.png %s" % additional_args)
            if res == 0:
                img_widget.value = open("./photo.png", "rb").read()
                with output:
                    output.clear_output()
                    print(time.ctime())
            else:
                with output:
                    output.clear_output()
                    print("raspistill command not working.")

            self.button.disabled = False
            self.button.description = "photo"

        self.button.on_click(on_button_clicked)
        self.widget = VBox([HBox([self.button, self.vflip, self.hflip]), output, img_widget])
