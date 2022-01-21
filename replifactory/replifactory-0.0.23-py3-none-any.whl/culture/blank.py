import numpy as np
import threading
import os
from replifactory.util import write_variable
from replifactory.loading import save_object, load_config
from replifactory.culture.plotting import plot_culture
import ipywidgets as widgets


from replifactory.culture.culture_functions import is_active
from replifactory.util import read_csv_tail


class BlankCulture:
    pumps = (1, 4)

    def __init__(self, directory: str = None, vial_number: int = None, name: str ="Blank",
                 description: str ="control vial, not inoculated"):
        self.vial_number = vial_number
        self.directory = None
        if directory is not None:
            self.directory = os.path.realpath(directory)
            if not self.directory[:-1].endswith("vial_"):
                self.directory = os.path.join(self.directory, "vial_%d" % vial_number)

        self.name = name
        self.description = description

        self.file_lock = threading.Lock()
        self._device = None
        self.dead_volume = 15  # volume below vacuum needle
        self.od_blank = 0
        self._od = None
        self._od_raw = None

    def update(self):
        pass

    @property
    def parameters(self):
        return sorted([k for k in self.__dict__.keys() if not k.startswith("_")])

    @property
    def od(self):
        return np.float32(self._od)

    @od.setter
    def od(self, value):
        write_variable(culture=self, variable_name="od_plus_blank", value=value)
        self._od_raw = value
        self._od = np.float32(value - self.od_blank)
        write_variable(culture=self, variable_name="od", value=self._od)
        self.save()

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, dev):
        if dev is not None:
            if self.directory is not None:
                assert os.path.join(dev.directory, "vial_%d" % self.vial_number) == self.directory
        self._device = dev
        self.save()

    def save(self):
        """
        saves config to vial_directory/culture_config.yaml
        """
        self.file_lock.acquire()  # maybe not necessary?
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        config_path = os.path.join(self.directory, "culture_config.yaml")

        save_object(self, filepath=config_path)
        self.file_lock.release()

    def write_blank_od(self):
        od_plus_blank_filepath = os.path.join(self.directory, "od_plus_blank.csv")
        df = read_csv_tail(filepath=od_plus_blank_filepath, lines=5)
        self.od_blank = df.values.ravel().mean()
        self.save()

    def load(self):
        config_path = os.path.join(self.directory, "culture_config.yaml")
        self.file_lock.acquire()
        try:
            load_config(self, filepath=config_path)
            print("Loaded vial %d config." % self.vial_number)
        finally:
            self.file_lock.release()

    def plot(self, last_hours=24, plot_growth_rate=False):
        fig = plot_culture(culture=self, last_hours=last_hours, plot_growth_rate=plot_growth_rate)
        return fig

    def is_active(self):
        if type(self) is BlankCulture:
            return False
        else:
            return is_active(culture=self)

    def show_parameters(self, increase_verbosity=False):
        if increase_verbosity:
            keys = [k for k in self.__dict__.keys() if not k.startswith("_")]
            keys = [k for k in keys if k not in ["directory", "file_lock"]]
            for k in sorted(keys):
                print("%s:" % k, self.__dict__[k])
        else:
            print("Vial %d: BLANK culture" % self.vial_number)

    # def handle_value_change(self, change):
    #     parameter_name = change.owner.description
    #     self.__dict__[parameter_name] = change.new
    #     self.save()

    def check(self):
        assert self.device.is_connected()
        assert self.vial_number in [1, 2, 3, 4, 5, 6, 7]
        assert os.path.exists(self.directory)
        assert 0 < self.dead_volume <= 35
        assert callable(self.device.od_sensors[self.vial_number].calibration_function)
        assert callable(self.device.pump1.calibration_function)
        assert callable(self.device.pump4.calibration_function)
        assert -0.3 < self.od_blank < 0.3
        self.device.stirrers.check_calibration(self.vial_number)

    # @property
    # def widget(self):
    #     user_parameters = [k for k in self.__dict__.keys() if not k.startswith("_") and
    #                        k not in ["name", "description", "directory", "file_lock", "vial_number", "pumps"]]
    #     parameter_style = {'description_width': '230px'}
    #     parameter_widgets = [widgets.FloatText(value=self.__dict__[par], description=par, style=parameter_style,
    #                                            continuous_update=True) for par in user_parameters]
    #     for w in parameter_widgets:
    #         w.observe(self.handle_value_change, names="value")
    #     parameter_box = widgets.VBox(parameter_widgets)
    #
    #     # description_style = {}
    #     # description_widgets = [widgets.HTML('<b>Vial %d:</b>' % self.vial_number, layout=Layout(width="40px")),
    #     #                        widgets.Text(value=self.name, description="name", style=description_style, continuous_update=True),
    #     #                        widgets.Textarea(value=self.description, description="description",
    #     #                                         style=description_style, continuous_update=True)]
    #     # for w in description_widgets:
    #     #     w.observe(self.handle_value_change, names="value")
    #     # description_box = widgets.VBox(description_widgets)
    #     # widgets.HBox([description_box, parameter_box])
    #     return parameter_box
