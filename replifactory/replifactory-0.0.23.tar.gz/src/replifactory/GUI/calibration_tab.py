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


class CalibrationTab:
    def __init__(self, main_gui):
        self.title = "Calibration"
        self.main_gui = main_gui

        config_paths = glob.glob("../**/device_config.yaml", recursive=True)
        config_paths = [os.path.join(p, "..") for p in config_paths]
        self.config_paths = [os.path.relpath(p) for p in config_paths]
        self.dev_config_dir = widgets.Dropdown(options=self.config_paths, description="source",
                                               style={"description_width": "initial"}, index=None)

        self.load_calibration = widgets.Button(description="load calibration", icon="fa-file-upload")
        self.load_calibration.on_click(self.handle_load_calibration_button)
        self.fit_functions = widgets.Button(description="fit calibration functions", icon="fa-cogs")
        self.fit_functions.on_click(self.handle_fit_calibration_button)
        self.button = widgets.Button(description="parameters", icon="fa-sliders-h")
        self.button.on_click(self.handle_button_click)
        self.output = widgets.Output()
        self.widget = VBox([HBox([self.dev_config_dir, self.load_calibration]), self.fit_functions, self.button, self.output])
        self.update()

    def handle_fit_calibration_button(self, b):
        with self.main_gui.status_bar.output:
            self.main_gui.device.fit_calibration_functions()

    def handle_button_click(self, button):
        self.update_paths()
        self.update()

    def handle_load_calibration_button(self, b):
        with self.main_gui.status_bar.output:
            path = os.path.join(self.dev_config_dir.value, "device_config.yaml")
            self.main_gui.experiment.device.load_calibration(path)
            if os.path.exists(self.main_gui.experiment.device.directory):
                self.main_gui.experiment.device.save()
                print("Saved calibration data to experiment directory: \n%s" % os.path.relpath(self.main_gui.experiment.device.directory))

    def update_paths(self):
        config_paths = glob.glob("../**/device_config.yaml", recursive=True)
        config_paths = [os.path.join(p, "..") for p in config_paths]
        self.config_paths = [os.path.relpath(p) for p in config_paths]

        self.dev_config_dir.options = [None] + self.config_paths

    def update(self):
        if self.main_gui.device is not None:
            with self.output:
                clear_output()
                time.sleep(0.1)
                stirrer_calibration = StirrerWidgets(self.main_gui.device).widget
                pump_calibration = CalibratePump(self.main_gui.device).widget
                od_calibration = CalibrateOD(self.main_gui.device).widget
                w = widgets.Accordion([od_calibration, stirrer_calibration, pump_calibration])
                w.set_title(0, "Optical Density")
                w.set_title(1, "Stirrers")
                w.set_title(2, "Pumps")
                display(w)
                # for od_sensor in self.main_gui.device.od_sensors.values():
                #     od_sensor.calibration_curve()
                #     plt.show()
                # self.main_gui.device.show_parameters()
        else:
            with self.output:
                clear_output()
                time.sleep(0.1)
                print("No device available")


class InputWidget:
    def __init__(self, q):
        self.name = q
        self.input = widgets.FloatText(description=q, style={'description_width': 'initial'})
        self.submit = widgets.Button(description="submit")
        self.widget = HBox([self.input, self.submit])


class CalibratePump:
    def __init__(self, device):
        layout = Layout(display='flex', width='300px')
        style = {'description_width': '120px'}
        self.device = device
        self.pump_number = widgets.Dropdown(description="Pump",
                                            description_tooltip="Pump number\n1: Fresh medium\n\
                                            2: Drug1 medium\n3: Drug2 medium\n4: Waste vacuum",
                                            options=[1, 2, 3, 4], index=None, style=style, layout=layout,
                                            continuous_update=False)
        self.stock_volume = widgets.FloatText(description="stock volume",
                                              description_tooltip="Volume available for pumping\n\
                                              (free volume in waste bottle)",
                                              style=style, layout=layout)
        self.stock_concentration = widgets.FloatText(description="stock concentration",
                                                     description_tooltip="leave empty for fresh medium and waste",
                                                     style=style, layout=layout)
        self.calibration_label = widgets.HTML('<b>Pump calibration:</b>\n place a vial on scales and measure the \
        pumped volume to calibrate the pumps. Repeat the measurement between 1-100 rotations to build a multipoint \
        calibration curve that accounts for pressure buildup during longer, faster pump runs',
                                              style=style, layout=Layout(width="600px"))

        #         self.calibration_label = widgets.Label("""""")
        self.rotations = widgets.FloatText(description="rotations",
                                           description_tooltip="number of rotations of pump head",
                                           style=style, layout=layout)
        self.iterations = widgets.IntText(description="iterations",
                                          description_tooltip="number of repetitions for averaging \
                                          pumped volume measurement",
                                          style=style, layout=layout)
        self.vial = widgets.Dropdown(description="Vial", description_tooltip="Vial to pump into",
                                     options=[1, 2, 3, 4, 5, 6, 7], style=style, layout=layout)
        self.vial.observe(self.update_vial)
        self.output = widgets.Output()
        self.output2 = widgets.Output()
        self.run_button = widgets.Button(description="RUN", button_style="danger")
        self.plot_button = widgets.Button(description="plot")

        args = VBox([self.pump_number, self.stock_volume, self.stock_concentration, self.calibration_label,
                     self.vial, self.rotations, self.iterations, self.output, self.run_button])
        self.widget = VBox([args, self.output2], style=style, layout=Layout(display='flex',
                                                               flex_flow='column',
                                                               border='solid',
                                                               width='720px'))

        self.pump_number.observe(self.update_pump)
        self.rotations.observe(self.update)
        self.iterations.observe(self.update)
        self.stock_concentration.observe(self.update_stock_concentration)
        self.stock_volume.observe(self.update_stock_volume)
        self.run_button.on_click(self.run)
        self.update(0)

    @property
    def pump(self):
        return self.device.pumps[self.pump_number.value]

    def update_vial(self, change):
        vial = self.vial.value
        assert not self.device.is_pumping()
        for valve in range(1, 8):
            if self.device.valves.is_open[valve] or self.device.valves.is_open[valve] is None:
                if valve != self.vial.value:
                    self.device.valves.close(valve=valve)
        self.device.valves.open(valve=self.vial.value)

    def update_pump(self, change):
        self.update(0)
        if self.pump_number.value in [1, 2, 3, 4]:
            self.stock_concentration.value = self.pump.stock_concentration
            self.stock_volume.value = self.pump.stock_volume
            self.generate_plot()

    def update_stock_volume(self, change):
        self.pump.stock_volume = self.stock_volume.value

    def update_stock_concentration(self, change):
        if self.stock_concentration.value is not None:
            self.pump.stock_concentration = self.stock_concentration.value

    def update(self, change):
        if self.pump_number.value in [1, 2, 3, 4]:
            with self.output:
                clear_output()
                pump_number = self.pump_number.value
                n_rotations = self.rotations.value
                n_iterations = self.iterations.value

                print("Pump %d will make %.1f rotations %d times" % (pump_number, n_rotations, n_iterations))
                pump = self.device.pumps[pump_number]
                total_volume = n_rotations * n_iterations * 0.2  # initial estimate
                pump.fit_calibration_function()
                if callable(pump.calibration_function):
                    def opt_function(volume):
                        return pump.calibration_function(volume) - n_rotations

                    predicted_mls = fsolve(opt_function, 1)[0]
                    predicted_total_mls = predicted_mls * n_iterations
                    total_volume = predicted_total_mls
                print("  (volume: ~%.2f mL)" % total_volume)

    def print_data(self):
        cd = self.device.calibration_pump_rotations_to_ml[self.pump_number.value]
        for k in sorted(cd.keys()):
            rots = k
            ml = cd[k]
            mlperrot = ml / rots
            print("%.3f mL/rotation @ %.2f rotations: " % (mlperrot, rots))

    def generate_plot(self):
        pump_number = self.pump_number.value
        pump = self.device.pumps[pump_number]
        with self.output2:
            clear_output()
            self.print_data()
            pump.calibration_curve()
            plt.show()

    def run(self, button):
        n_rotations = self.rotations.value
        n_iterations = self.iterations.value

        with self.output:
            print("Pumping...")
            for i in range(n_iterations):
                self.pump.move(n_rotations)
                print("%d/%d" % (i + 1, n_iterations), end="\t\r")
                while self.pump.is_pumping():
                    time.sleep(0.1)
                time.sleep(0.5)
            mlinput = InputWidget("How many ml?")
            display(mlinput.widget)

            def on_submit(button):
                ml = mlinput.input.value
                ml = ml / n_iterations
                self.device.calibration_pump_rotations_to_ml[self.pump_number.value][n_rotations] = round(ml, 3)
                self.device.save()
                self.generate_plot()

            mlinput.submit.on_click(on_submit)


class CalibrateOD:
    def __init__(self, device):
        self.device = device
        self.text1 = widgets.HTML("""<b> 1. OD max: </b> prepare calibration standard with highest OD (close to measurement limit): <br>
                                1.1. Add <b>30mL</b> water and a stirrer bar in vial 1 <br>
                                1.2. Stir gently. Set stirrer speed so vortex does not reach the laser level <br>
                                1.3. Add milk drops to vial 1 until the signal is about 1 mV.<br>
                                """)
        self.min_signal_button = widgets.Button(description="measure signal 1")
        self.stirrer1_slider = widgets.FloatSlider(description="stirrer1 speed", value=0, min=0, max=1, step=0.01,
                                                   continuous_update=False)
        self.output = widgets.Output()
        self.stirrer1_slider.observe(self.set_stirrer1_speed)
        self.min_signal_button.on_click(self.measure_signal1)
        self.widget1 = VBox([self.text1, self.stirrer1_slider, HBox([self.min_signal_button, self.output])])

        self.text2 = widgets.HTML("""<b> 2. Serial dilution: </b> prepare remaining calibration standards<br>
                                2.1. Add <b>15mL</b> water and a stirrer bar in 6 more vials <br>
                                2.2. Stir gently. Calibrate the stirrer speed if necessary. <br>
                                2.3. Transfer 15mL from vial 1 to vial 2, then from vial 2 to vial 3, etc.<br>
                                """)
        self.stirrers_widget = StirrerWidgets(self.device).widget
        self.widget2 = VBox([self.text2, self.stirrers_widget])

        self.text3 = widgets.HTML("""<b> 3. Determine OD of calibration standards: </b> measure directly or calculate<br>
        3.1. Using a calibrated lab device, measure the OD in some of the vials (within the working range of the device).<br>
        3.2. Calculate the remaining OD values by fitting a line through the measured values.<br>
        3.3. Use clean medium for vial 14 (OD 0).<br>""")
        self.probe_OD_input = VBox(
            [widgets.FloatText(description="probe %d OD" % i, layout=Layout(width="150px"), value=np.nan, step=0.01,
                               style={'description_width': '80px'}) for i in range(1, 15)])
        self.probe_OD_input.children[-1].value = 0
        self.probe_OD_input.children[-1].disabled = True
        self.probe_OD_input.children[-1].description_tooltip = "Please make sure vial 14 is clean medium"
        self.OD_values_fitted = VBox(
            [widgets.FloatText(description="fit:", layout=Layout(width="120px"), value=np.nan, disabled=True,
                               style={'description_width': '40px'}) for i in range(1, 15)])

        self.probe_od_input_clear_button = widgets.Button(description="clear", tooltip="clear all fields")
        self.probe_od_input_clear_button.on_click(self.clear_probe_ods)
        self.fit_probe_ods_button = widgets.Button(description="fit", tooltip="fit line and calculate all OD values")
        self.fit_probe_ods_button.on_click(self.fit_probe_ods)
        self.buttons3 = HBox([self.probe_od_input_clear_button, self.fit_probe_ods_button])
        self.widget3 = VBox([self.text3, HBox([self.probe_OD_input, self.OD_values_fitted]), self.buttons3])

        self.text4 = widgets.HTML("""<b> 4. Measure signal of each OD sensor with each probe: </b> cycle all probes in 2 batches of 7<br>
        4.1. Place first 7 probes in the device<br>
        4.2. Measure signal in all OD sensors<br>
        4.3. Remove probe 7, shift the probes to the right by 1 (place probe 6 in OD sensor 7, probe 5 in OD sensor 6 ...) then place probe 7 in OD sensor 1<br>
        4.4. Measure signal in all OD sensors, repeat steps 2-3 to cover all 7 combinations.<br>
        4.5. Place remaining 7 probes in the device and repeat steps 2-4 for the second batch.
        """)
        self.probe_group_selector = widgets.Dropdown(description="probes", options=["1-7", "8-14"], index=None)
        self.prev_batch_button = widgets.Button(description="<< previous", tooltip="shift probes left")
        self.measure_signals_button = widgets.Button(description="measure", tooltip="measure and log signal in all OD sensors")
        self.next_batch_button = widgets.Button(description="next >>", tooltip="shift probes right")
        self.prev_batch_button.on_click(self.prev_switch)
        self.next_batch_button.on_click(self.next_switch)
        self.measure_signals_button.on_click(self.measure_all)
        self.fit_curve_button = widgets.Button(description="fit function", tooltip="fit calibration function")
        self.fit_curve_button.on_click(self.fit_functions)
        self.plot_curve_button = widgets.Button(description="plot calibration", tooltip="plot calibration curve")
        self.plot_curve_button.on_click(self.plot_curves)

        self.probe_group_selector.observe(self.select_probe_group)
        self.buttons4 = VBox([HBox([self.probe_group_selector, self.prev_batch_button, self.measure_signals_button,
                              self.next_batch_button]), HBox([self.fit_curve_button, self.plot_curve_button])])
        self.output4 = widgets.Output()
        self.widget4 = VBox([self.text4, self.buttons4, self.output4])

        self.widget = VBox([self.widget1, self.widget2, self.widget3, self.widget4])

    def clear_probe_ods(self, button):
        for c in self.probe_OD_input.children[:-1]:
            c.value = np.nan
        for c in self.OD_values_fitted.children[:-1]:
            c.value = np.nan

    def fit_probe_ods(self, button):
        probe_nrs = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        OD_values = np.array([c.value for c in self.probe_OD_input.children])
        mask = ~np.isnan(OD_values)
        mask[-1] = False
        probe_nrs = probe_nrs[mask]
        OD_values = OD_values[mask]

        p = np.polyfit(probe_nrs, np.log2(OD_values), 1)
        probe_nr_to_od = {probe: round(2 ** np.poly1d(p)(probe), 3) for probe in range(1, 15)}
        probe_nr_to_od[14] = 0
        self.probe_nr_to_od = probe_nr_to_od
        for i in range(14):
            self.OD_values_fitted.children[i].value = probe_nr_to_od[i + 1]

    def set_stirrer1_speed(self, slider):
        self.device.stirrers._set_duty_cycle(1, self.stirrer1_slider.value)

    def measure_signal1(self, button):
        with self.output:
            clear_output()
            try:
                signal = self.device.od_sensors[1].measure_signal()
                print("Signal: %.3f mV" % signal)
            except:
                print("signal measurement error")

    def select_probe_group(self, dropdown):
        if self.probe_group_selector.value:
            if self.probe_group_selector.value[0] == "1":
                self.probes = list(range(1, 8))
            if self.probe_group_selector.value[0] == "8":
                self.probes = list(range(8, 15))
            self.vial_nr_to_probe = dict(zip(range(1, 8), self.probes))
            self.print_probe_order()

    def prev_switch(self, button):
        self.probes = self.probes[1:] + [self.probes[0]]  # shift left
        self.vial_nr_to_probe = dict(zip(range(1, 8), self.probes))
        self.print_probe_order()

    def next_switch(self, button):
        self.probes = [self.probes[6]] + self.probes[:6]  # shift right
        self.vial_nr_to_probe = dict(zip(range(1, 8), self.probes))
        self.print_probe_order()

    def print_probe_order(self):
        with self.output4:
            clear_output()
            print("OD sensor:   ", "  ".join("%5d" % i for i in self.vial_nr_to_probe.keys()))
            print("Probe nr:    ", "  ".join("%5d" % i for i in self.vial_nr_to_probe.values()))
            ods = [self.probe_nr_to_od[self.vial_nr_to_probe[v]] for v in range(1, 8)]
            print("OD value:    ", " ".join("%.3f" % i for i in ods))

    def measure_all(self, button):
        with self.output4:
            clear_output()
            for v in range(1, 8):
                probe_nr = self.vial_nr_to_probe[v]
                od = self.probe_nr_to_od[probe_nr]
                try:
                    signal = self.device.od_sensors[v].measure_signal()
                    print("Signal: %.3f mV" % signal)
                    self.device.od_sensors[v].add_calibration_point(od=od, mv=signal)
                    print("OD sensor %d probe %d:   %.3fmv  OD %.3f" % (v, probe_nr, signal, od))
                except:
                    print("signal measurement error")
                self.device.save()
            print(self.device.calibration_od_to_mv)

    def fit_functions(self, button):
        for v in range(1,8):
            self.device.od_sensors[v].fit_calibration_function()

    def plot_curves(self,button):
        with self.output4:
            clear_output()
            for v in range(1,8):
                self.device.od_sensors[v].plot_calibration_curve()
                plt.show()
