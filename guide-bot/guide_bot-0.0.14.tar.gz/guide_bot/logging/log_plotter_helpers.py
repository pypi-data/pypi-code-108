class LogParameter:
    def __init__(self):
        self.name = None
        self.owner = None
        self.type = None
        self.limits = None

    def read_line(self, line):
        """
        self.name = line[0:50].strip() # name.ljust(60)
        self.owner = line[50:50+30].strip()
        self.type = line[50+30:50+30+60].strip()
        self.limits = line[50+30+60:].strip().split(",")
        """

        line_parts = line.split()

        self.name = line_parts[0].strip()
        self.owner = line_parts[1].strip()
        self.type = line_parts[2].strip()

        if len(line_parts) > 4:
            self.limits = [line_parts[3].strip().strip(","), line_parts[4].strip()]
        else:
            self.limits = ""

    def __repr__(self):
        if isinstance(self.limits, list) and len(self.limits) == 2:
            return self.name + " " + self.owner + " " + self.type + " " + self.limits[0] + ", " + self.limits[1]
        else:
            return self.name + " " + self.owner + " " + self.type


class GuideElementLog:
    def __init__(self, element_name, element_type):
        self.element_name = element_name
        self.element_type = element_type
        self.parameter_type = {}
        self.parameters = {}

    def add_parameter(self, key, type, value):
        self.parameter_type[key] = type
        self.parameters[key] = value


def sort_permutation(input, **kwargs):
    L = [(input[i], i) for i in range(len(input))]
    L.sort(**kwargs)
    sorted_start_points_first, permutation = zip(*L)
    return list(permutation)


def extract_parameters(guide_element, legend, data_line):

    return_dict = {}
    for simple_name in guide_element.parameters:
        instrument_parameter_name = guide_element.parameters[simple_name]
        if instrument_parameter_name in legend:
            par_index = legend.index(instrument_parameter_name)
            par_value = data_line[par_index]

            return_dict[simple_name] = par_value

    return return_dict