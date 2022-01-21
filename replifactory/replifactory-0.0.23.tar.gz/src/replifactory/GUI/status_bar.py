import os
import glob
import ipywidgets as widgets

from ipywidgets import Layout, VBox, HBox

from replifactory.GUI.device_tab import get_ftdi_addresses
from replifactory.experiment import Experiment

from IPython.display import clear_output, display

# class ExperimentWidget:
#     def __init__(self, status_bar):
#         self.status_bar = status_bar
#         print("output made")
#         with self.status_bar.output:
#             self.status_bar.main_gui.experiment = Experiment("NewExperiment")
#         # if self.status_bar.main_gui.experiment is not None:
#         #     with self.status_bar.output:
#         #         self.status_bar.main_gui.experiment.status()
# box_layout = Layout(display='flex',
#                     flex_flow='column',
#                     align_items='stretch',
#                     border='solid 1px gray', )


class StatusBar:
    layout_width = "350px"
    config_paths = glob.glob("../**/device_config.yaml", recursive=True)
    config_paths = [os.path.relpath(os.path.join(p, "..")) for p in config_paths]
    experiment_directories = glob.glob("../**/main_run.log", recursive=True)
    experiment_directories = [os.path.relpath(os.path.join(p, "..")) for p in experiment_directories]

    def __init__(self, main_gui):
        self.main_gui = main_gui
        ftdi_addresses = get_ftdi_addresses()
        ndev = len(ftdi_addresses)
        self.output = widgets.Output()
        self.output.layout.width = "340px"
        self.head = widgets.Accordion(layout=Layout(width=self.layout_width))
        self.head.set_title(0, "Status")

        self.check_button = widgets.Button(description="TEST", icon="fa-clipboard-check")
        self.run_button = widgets.Button(description="RUN", icon="fa-play", disabled=True)
        self.stop_button = widgets.Button(description="STOP", icon="fa-stop", disabled=True)

        self.check_button.on_click(self.handle_check_button)
        self.run_button.on_click(self.handle_run_button)
        self.stop_button.on_click(self.handle_stop_button)

        self.exp_dir = widgets.Dropdown(options=self.experiment_directories, description="Experiment",
                                        style={"description_width": "initial"}, index=None)

        # self.new_exp_folder = widgets.Text(description="new experiment directory:",
        #                                    style={"description_width": "initial"})
        self.make_new_exp = widgets.Button(description="", icon="fa-folder-plus", layout=Layout(width='35px'))
        self.make_new_exp.on_click(self.handle_new_experiment)
        self.exp_dir.observe(self.handle_experiment_folder_choice, names="value")

        self.input = None
        widget_list = [HBox([self.exp_dir, self.make_new_exp]),
                       self.check_button, HBox([self.run_button, self.stop_button])]
        self.head.children = [VBox(widget_list)]
        self.clear_output_button = widgets.Button(description="clear output", icon="fa-eraser")
        self.clear_output_button.on_click(self.handle_clear_output_button)
        self.widget = VBox([self.head, self.clear_output_button, self.output])

        # self.update()

    # def ask_question(self, question):
    #     input_label = widgets.Label("How can i help you? ")
    #     input_text = widgets.Text()

    def handle_clear_output_button(self,b):
        with self.output:
            clear_output()

    def update_paths(self):
        self.exp_dir.unobserve_all()

        config_paths = glob.glob("../**/device_config.yaml", recursive=True)
        self.config_paths = [os.path.relpath(p) for p in config_paths]
        experiment_directories = glob.glob("../**/main_run.log", recursive=True)
        self.experiment_directories = [os.path.relpath(os.path.join(p, "..")) for p in experiment_directories]

        self.exp_dir = widgets.Dropdown(options=self.experiment_directories, description="Experiment",
                                        style={"description_width": "initial"}, index=None)
        self.exp_dir.index = self.exp_dir.options.index(os.path.relpath(self.main_gui.experiment.directory))
        self.exp_dir.observe(self.handle_experiment_folder_choice, names="value")
        self.update()

    def handle_check_button(self, b):
        with self.output:
            clear_output()
            assert not self.main_gui.experiment.is_running()
            self.main_gui.experiment.device.check_all()
            self.run_button.disabled = False
            # self.update()

    def handle_run_button(self, b):
        with self.output:
            clear_output()
            self.main_gui.experiment.run()
            self.run_button.disabled = True
            self.stop_button.disabled = False
            # self.update()

    def handle_stop_button(self, b):
        with self.output:
            clear_output()
            self.main_gui.experiment.stop()
            self.stop_button.disabled = True
            self.run_button.disabled = False
            # self.update()

    def update(self):
        widget_list = [HBox([self.exp_dir, self.make_new_exp]),
                       self.check_button, HBox([self.run_button, self.stop_button])]
        self.head.children = [VBox(widget_list)]
        self.main_gui.reload_status_bar_widget()
        # with self.subtitle:
        #     clear_output()
            # try:
            #     print("WORK DIRECTORY: %s" % self.main_gui.experiment.directory)
            # except:
            #     print("WORK DIRECTORY: None")
            # try:
            #     if self.main_gui.device.__class__ is type(None):
            #         print("  DEVICE CLASS: None")
            #     else:
            #         print("  DEVICE CLASS: %s" % str(self.main_gui.device.__class__).split(".")[-1][:-2])
            # except:
            #     print("  DEVICE CLASS: None")
            # try:
            #     print("DEVICE ADDRESS: %s" % self.main_gui.device.ftdi_address)
            # except:
            #     print("DEVICE ADDRESS: None")

        # widget_list = [self.title, self.subtitle,
        #                self.check_button, HBox([self.run_button, self.stop_button]),
        #                HBox([self.load_exp, self.make_new_exp]),
        #                self.output_title, self.output]
        # self.widget = VBox(widget_list, layout=Layout(width=self.layout_width))
        # self.main_gui.reload_status_bar_widget()

    def handle_new_experiment(self, b):
        # if self.main_gui.device is None:
        #     with self.output:
        #         print("PLEASE CONNECT DEVICE TO CREATE NEW EXPERIMENT!")
        # else:
        with self.output:
            clear_output()
            self.q = widgets.Text(description="new directory:", continuous_update=False)
            b = widgets.Button(description="create directory")
            display(VBox([self.q, b]))
            b.on_click(self.make_new_exp_folder)

    def make_new_exp_folder(self, change):
        directory = self.q.value
        with self.output:
            print("Creating new experiment")
            self.main_gui.experiment = Experiment(directory)
            self.update()
            self.main_gui.experiment_tab.update()
        self.update_paths()

    def handle_experiment_folder_choice(self, change):
        directory = change.new
        with self.output:
            clear_output()
            self.main_gui.experiment = Experiment(directory)
        self.update()
        self.main_gui.experiment_tab.update()


class InputWidget:
    def __init__(self, q):
        self.name = q
        self.input = widgets.FloatText(description=q, style={'description_width': 'initial'})
        self.submit = widgets.Button(description="submit")
        self.widget = HBox([self.input, self.submit])


class UserInputFloat:
    def __init__(self, status_bar, question, action=None):
        self.status_bar = status_bar
        self.question = question
        self.action = action
        with self.status_bar.output:
            clear_output()
            q = widgets.FloatText(description=question, continuous_update=False)
            display(q)
        q.observe(self.on_answer, names="value")

    def on_answer(self, change):
        with self.status_bar.output:
            clear_output()
            print(self.question, "\nuser input:", change.new)
            if self.action is callable:
                self.action(change.new)


class UserInputText:
    def __init__(self, status_bar, question, action=None):
        self.status_bar = status_bar
        self.question = question
        self.action = action
        with self.status_bar.output:
            clear_output()
            q = widgets.Text(description=question, continuous_update=False)
            display(q)
        q.observe(self.on_answer, names="value")

    def on_answer(self, change):
        with self.status_bar.output:
            clear_output()
            print(self.question, "\nuser input:", change.new)
            if self.action is callable:
                print("calling")
                self.action(change.new)


class UserInputConfirm:
    def __init__(self, status_bar, question, action=None):
        self.status_bar = status_bar
        self.question = question
        self.action = action
        with self.status_bar.output:
            clear_output()
            y = widgets.Button(description="Yes", button_style="success")
            n = widgets.Button(description="No", button_style="danger")
            q = HBox([y, n])
            display(q)
        y.on_click(self.on_yes)
        n.on_click(self.on_no)

    def on_yes(self, button):
        with self.status_bar.output:
            clear_output()
            print("yass")

    def on_no(self, button):
        with self.status_bar.output:
            clear_output()
            print("nope")
