import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from operator import itemgetter

class SystemParameterFigureGenerator():

    def __init__(self, system_parameters: str):

        self.__fig = go.Figure
        self.__system_parameters = system_parameters
        self.__system_parameters_dict: dict = dict()
        self.__max_number_DC_subsystems: int = int()
        self.__grid_height: int = 0
        self.__grid_width: int = 0
        # system parameters keys
        self.__subsystem = 'subsystems'
        self.__acdc_converter = "acdc_converter"
        self.__power_distribution = "power_distribution"
        self.__dcdc_converter = "dcdc_converter"
        self.cell_type = "cell_type"
        self.__technology = "technology"
        self.__id = "id"
        # Grid elements
        self.__spec: list = list()
        self.__AC_IDs: list = list()
        self.__DC_tech: list = list()
        self.__DCDC_converters: list = list()
        self.__ACDC_converters: list = list()
        self.__DC_power_distribution: list = list()
        self.__grid_pos_AC_IDs: list = list()
        self.__grid_pos_DC_power_distribution: list = list()
        self.__grid_pos_DC_tech: list = list()

    def generate(self):
        self.system_parameters_as_dict()
        self.grid_generator()
        self.annotation_generator()
        self.figure_generator()
        self.boxes_generator()
        self.boxes_filler()
        self.beautify_fig()
        return self.__fig

    def system_parameters_as_dict(self):
        with open(self.__system_parameters, 'r') as system_parameters:
            lines: [str] = system_parameters.readlines()
            __system_parameters_str = ""
            for line in lines:
                __system_parameters_str += line
            system_parameters_as_string = __system_parameters_str
            global system_parameters_as_dict
            system_parameters_as_dict = "global system_parameters_as_dict \nsystem_parameters_as_dict="
            exec(system_parameters_as_dict + system_parameters_as_string[22:])
            size_of_AC_systems = []
            for i in range(len(system_parameters_as_dict[self.__subsystem])):
                size_of_AC_systems.append(len(system_parameters_as_dict[self.__subsystem][i][self.__subsystem]))
            self.__max_number_DC_subsystems = max(size_of_AC_systems)
            self.__system_parameters_dict = system_parameters_as_dict

    def grid_generator(self):
        self.__grid_width = len(self.__system_parameters_dict[self.__subsystem]) * 3
        self.__grid_height = self.__max_number_DC_subsystems * 2 + 2
        AC_power_distribution = [{"colspan": self.__grid_width}]
        AC_power_distribution += [None] * (self.__grid_width - 1)
        AC_line = []
        DC_matrix = []
        for i in range(len(self.__system_parameters_dict[self.__subsystem])):
            AC_system = self.__system_parameters_dict[self.__subsystem][i]
            AC_line += [{"colspan": 3}, None, None]
            DC_power_distribution = [{"rowspan": self.__grid_height - 2}]
            DC_power_distribution += [None] * (self.__grid_height - 3)
            DC_columns = []
            for j in range(len(AC_system[self.__subsystem])):
                DC_columns += [{"colspan": 2, "rowspan": 2}, None]
            DC_col2 = [None] * len(AC_system[self.__subsystem] * 2)
            if len(DC_columns) < self.__grid_height - 2:
                dif = self.__grid_height - 2 - len(DC_columns)
                DC_columns += [None] * (dif)
                DC_col2 += [None] * (dif)
            DC_matrix.append(DC_power_distribution)
            DC_matrix.append(DC_columns)
            DC_matrix.append(DC_col2)
        DC_matrix = [[DC_matrix[j][i] for j in range(len(DC_matrix))] for i in range(len(DC_matrix[0]))]
        self.__spec.append(AC_power_distribution)
        self.__spec.append(AC_line)
        self.__spec.extend(DC_matrix)

    def annotation_generator(self):
        for i in range(len(self.__system_parameters_dict[self.__subsystem])):
            AC_system = self.__system_parameters_dict[self.__subsystem][i]
            self.__AC_IDs.append("AC_system " + AC_system['id'])
            self.__ACDC_converters.append(re.sub('([A-Z0-9])', r' \1', AC_system[self.__acdc_converter]))
            self.__DC_power_distribution.append(re.sub('([A-Z0-9])', r' \1', AC_system[self.__power_distribution]))
            for j in range(len(AC_system[self.__subsystem])):
                dc_system = AC_system[self.__subsystem][j]
                if self.cell_type in dc_system:
                    tech = re.sub('([A-Z0-9])', r'<br>\1', dc_system[self.__technology]) + " " + dc_system[
                        self.__id] + "<br>" + \
                           dc_system[self.cell_type]
                else:
                    tech = re.sub('([A-Z0-9])', r'<br>\1', dc_system[self.__technology]) + " " + dc_system[
                        self.__id]
                dcdc_converter = re.sub('([A-Z0-9])', r' \1', dc_system[self.__dcdc_converter])
                self.__DC_tech.append(tech)
                self.__DCDC_converters.append(dcdc_converter)

    def figure_generator(self):
        self.__fig = make_subplots(cols=self.__grid_width, rows=self.__grid_height, print_grid=False,
                                   specs=self.__spec, horizontal_spacing=0.02)

    def boxes_generator(self):
        for i in range(len(self.__spec)):
            for j in range(len(self.__spec[0])):
                grid = self.__spec[i][j]
                if grid != None:
                    self.__fig.add_trace(go.Scatter(x=[], y=[]), row=i + 1, col=j + 1)
                    if self.__spec[i][j] != None and grid["rowspan"] == (self.__grid_height - 2):
                        self.__grid_pos_DC_power_distribution.append((i + 1, j + 1))
                    if self.__spec[i][j] != None and grid["rowspan"] == 2 and grid["colspan"] == 2:
                        self.__grid_pos_DC_tech.append((i + 1, j + 1))
                    if self.__spec[i][j] != None and grid["colspan"] == 3:
                        self.__grid_pos_AC_IDs.append((i + 1, j + 1))
        self.__grid_pos_DC_tech.sort(key=itemgetter(1))
        # Handling the exception if there is only one AC system, or if the biggest AC system only has one DC subsystem
        if self.__grid_height == 4:
            self.__grid_pos_DC_power_distribution = self.__grid_pos_DC_power_distribution[::2]
        if self.__grid_width == 3:
            self.__grid_pos_AC_IDs = self.__grid_pos_AC_IDs[1::2]

    def boxes_filler(self):
        self.__fig.add_annotation(row=1, col=1, text=re.sub('([A-Z0-9])', r' \1', self.__system_parameters_dict[
            self.__power_distribution]), x=0.5,
                                  y=0.5, showarrow=False)
        for i in range(len(self.__grid_pos_AC_IDs)):
            self.__fig.add_annotation(row=self.__grid_pos_AC_IDs[i][0], col=self.__grid_pos_AC_IDs[i][1],
                                      text=self.__AC_IDs[i], x=0.5, y=0.5,
                                      showarrow=False)
        for i in range(len(self.__grid_pos_DC_power_distribution)):
            if self.__grid_height == 4:
                self.__fig.add_annotation(row=self.__grid_pos_DC_power_distribution[i][0],
                                          col=self.__grid_pos_DC_power_distribution[i][1],
                                          text=re.sub('([A-Z0-9])', r'<br>\1', self.__DC_power_distribution[i]),
                                          x=0.5, y=0.35, showarrow=False,
                                          font=dict(size=9))
                self.__fig.add_annotation(row=self.__grid_pos_DC_power_distribution[i][0],
                                          col=self.__grid_pos_DC_power_distribution[i][1],
                                          x=0.5, y=0.85, showarrow=False,
                                          text=re.sub('([A-Z0-9])', r'<br>\1',
                                                      self.__ACDC_converters[i].replace("Ac Dc", "ac-dc")),
                                          font=dict(size=8))
                self.__fig.add_shape(row=self.__grid_pos_DC_power_distribution[i][0],
                                     col=self.__grid_pos_DC_power_distribution[i][1],
                                     type="line", x0=0, y0=0.6, x1=1, y1=0.6,
                                     line=dict(color="White", width=3, dash="solid"))
            else:
                self.__fig.add_annotation(row=self.__grid_pos_DC_power_distribution[i][0],
                                          col=self.__grid_pos_DC_power_distribution[i][1],
                                          text=self.__DC_power_distribution[i], x=0.5, y=0.4, showarrow=False,
                                          textangle=270,
                                          font=dict(size=9 + self.__max_number_DC_subsystems))
                self.__fig.add_annotation(row=self.__grid_pos_DC_power_distribution[i][0],
                                          col=self.__grid_pos_DC_power_distribution[i][1],
                                          text=re.sub('([A-Z0-9])', r'<br>\1',
                                                      self.__ACDC_converters[i].replace("Ac Dc", "ac-dc")),
                                          x=0.5, y=0.9,
                                          showarrow=False, font=dict(size=8))
                self.__fig.add_shape(row=self.__grid_pos_DC_power_distribution[i][0],
                                     col=self.__grid_pos_DC_power_distribution[i][1],
                                     type="line", x0=0, y0=0.75, x1=1, y1=0.75,
                                     line=dict(color="White", width=3, dash="solid"))

        for i in range(len(self.__grid_pos_DC_tech)):
            self.__fig.add_annotation(row=self.__grid_pos_DC_tech[i][0], col=self.__grid_pos_DC_tech[i][1],
                                      text=self.__DC_tech[i], x=0.6, y=0.5,
                                      showarrow=False, font=dict(size=9))
            self.__fig.add_annotation(row=self.__grid_pos_DC_tech[i][0], col=self.__grid_pos_DC_tech[i][1],
                                      text=re.sub('([A-Z0-9])', r'<br>\1',
                                                  self.__DCDC_converters[i].replace("Dc Dc", "dc-dc")),
                                      x=0.1, y=0.5, showarrow=False, font=dict(size=9), textangle=270)
            self.__fig.add_shape(row=self.__grid_pos_DC_tech[i][0], col=self.__grid_pos_DC_tech[i][1], type="line",
                                 x0=0.25, y0=0, x1=0.25, y1=1, line=dict(color="White", width=3, dash="solid"))

    def beautify_fig(self):
        self.__fig.update_xaxes(range=[0, 1], showticklabels=False, showgrid=False, zeroline=False, fixedrange=True)
        self.__fig.update_yaxes(range=[0, 1], showticklabels=False, showgrid=False, zeroline=False, fixedrange=True)
        # self.__fig.update_layout(width=self.__grid_width * 90 + 350, height=self.__grid_height * 90,automargin=True)
        self.__fig.update_layout(autosize=True)
