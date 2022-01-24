import numpy as np

from guide_bot.base_elements import guide_elements
from guide_bot.parameters import instrument_parameters as ipars

from guide_bot.base_elements.guide_elements import PositionAndRotation

class Elliptic(guide_elements.GuideElement):
    """
    Elliptic GuideElement that inserts an elliptic section into a guide

    The elliptic guide needs to have start and end dimensions set to fit
    into the guide_bot logic, so the focal points are determined by these
    dimensions and the minor_axis in each direction. The minor_axis can be
    limited or specified as the normal Element parameters. In addition it
    is possible to set a maximum width / height of the element for cases
    where the guide has to fit within a narrow space. The minor axis can
    be greater than the maximum width of the guide, as only a segment of
    the full ellipse is simulated, and the minor axis might be outside
    that segment. If end_width or end_height is specified, they will
    override the  start_width or start_height setting of the next Element
    in the guide.
    """
    def __init__(self, name, length=None, start_point=None, start_width=None, start_height=None,
                 end_width=None, end_height=None, minor_axis_x=None, minor_axis_y=None,
                 max_width=None, max_height=None,  **kwargs):
        """
        Elliptic GuideElement that inserts an elliptic section into a guide

        The elliptic guide needs to have start and end dimensions set to fit
        into the guide_bot logic, so the focal points are determined by these
        dimensions and the minor_axis in each direction. The minor_axis can be
        limited or specified as the normal Element parameters. In addition it
        is possible to set a maximum width / height of the element for cases
        where the guide has to fit within a narrow space. The minor axis can
        be greater than the maximum width of the guide, as only a segment of
        the full ellipse is simulated, and the minor axis might be outside
        that segment. If end_width or end_height is specified, they will
        override the  start_width or start_height setting of the next Element
        in the guide.

        Parameters
        ----------
        name : str
            Name of the element

        length : (float, None, InstrumentParameter)
            Length of guide element, optimized parameter

        start_point : (float, None, InstrumentParameter)
            Distance from source to start of the gap element

        start_width : (float, None, InstrumentParameter)
            Width of the start of the gap

        start_height : (float, None, InstrumentParameter)
            Height of the start of the gap

        end_width : (float, None, InstrumentParameter)
            Width of the end of the gap

        end_height : (float, None, InstrumentParameter)
            Height of the end of the gap

        minor_axis_x : (float, None, InstrumentParameter)
            Minor axis of the full ellipse, horizontal direction

        minor_axis_y : (float, None, InstrumentParameter)
            Minor axis of the full ellipse, vertical direction

        max_width : float
            Maximum width of the inserted guide segment

        max_height : float
            Maximum height of the inserted guide segment
        """
        # Record if the parameters are given by the user or not
        self.start_width_custom_parameter = isinstance(start_width, ipars.InstrumentParameter)
        self.minor_axis_x_custom_parameter = isinstance(minor_axis_x, ipars.InstrumentParameter)
        self.end_width_custom_parameter = isinstance(end_width, ipars.InstrumentParameter)

        self.start_height_custom_parameter = isinstance(start_height, ipars.InstrumentParameter)
        self.minor_axis_y_custom_parameter = isinstance(minor_axis_y, ipars.InstrumentParameter)
        self.end_height_custom_parameter = isinstance(end_height, ipars.InstrumentParameter)

        super().__init__(name, length=length, start_point=start_point,
                         start_width=start_width, start_height=start_height,
                         end_width=end_width, end_height=end_height,
                         **kwargs)


        self.max_width = max_width
        if self.max_width is None:
            max_width = 0.3

        if isinstance(minor_axis_x, ipars.InstrumentParameter):
            self.minor_axis_x = minor_axis_x
        else:
            self.minor_axis_x = guide_elements.handle_input_parameter(name + "_minor_axis_x", minor_axis_x,
                                                                      default_min=-0.3, default_max=max_width)

            # Trying build where all parameters are RelativeFree, no need to replace
            """
            # Replace with a RelativeFreeParameter to control illegal intervals
            if isinstance(self.minor_axis_x, ipars.FreeInstrumentParameter):
                min_value = self.minor_axis_x.get_lower_bound()
                max_value = self.minor_axis_x.get_upper_bound()

                self.minor_axis_x = ipars.RelativeFreeInstrumentParameter(name + "_minor_axis_x", min_value, max_value)
            """

        self.max_height = max_height
        if self.max_height is None:
            max_height = 0.3

        if isinstance(minor_axis_y, ipars.InstrumentParameter):
            self.minor_axis_y = minor_axis_y
        else:
            self.minor_axis_y = guide_elements.handle_input_parameter(name + "_minor_axis_y", minor_axis_y,
                                                                      default_min=-0.3, default_max=max_height)

            # Trying build where all parameters are RelativeFree, no need to replace
            """
            # Replace with a RelativeFreeParameter to control illegal intervals
            if isinstance(self.minor_axis_y, ipars.FreeInstrumentParameter):
                min_value = self.minor_axis_y.get_lower_bound()
                max_value = self.minor_axis_y.get_upper_bound()

                self.minor_axis_y = ipars.RelativeFreeInstrumentParameter(name + "_minor_axis_y", min_value, max_value)
            """

        # temporary reflectivity model
        if "R0" in kwargs:
            self.R0 = kwargs["R0"]
        else:
            self.R0 = 0.99

        if "Qc" in kwargs:
            self.Qc = kwargs["Qc"]
        else:
            self.Qc = 0.0217

        if "alpha" in kwargs:
            self.alpha = kwargs["alpha"]
        else:
            self.alpha = 6.07

        if "m" in kwargs:
            self.m = kwargs["m"]
        else:
            self.m = 1.0

        if "W" in kwargs:
            self.W = kwargs["W"]
        else:
            self.W = 0.003

        if "enableGravity" in kwargs:
            self.enableGravity = kwargs["enableGravity"]
        else:
            self.enableGravity = 1

    def write_to_log(self, file):
        self.write_to_log_base(file)
        self.write_parameter(file, "minor_axis_x", self.minor_axis_x, "horizontal")
        self.write_parameter(file, "minor_axis_y", self.minor_axis_y, "vertical")

    def add_to_instr(self):
        """
        Adds code describing the elliptic element to the current McStas instrument

        This methods uses McStasScript to add components and code to a McStas
        instrument object. The McStas instrument object is an attribute of the
        class called current_instrument. New instrument parameters can also be
        created and added to the optimization by using the current_parameters
        attribute.

        Since the add_to_instr method of all the Elements are called in order
        from the sample to the source, it is important the components are
        added after the Origin component to ensure the correct order.
        """

        if self.minor_axis_x_custom_parameter:
            # Attempt to set limits on start and end (except if the two parameters are the same)
            if isinstance(self.start_width, ipars.RelativeFreeInstrumentParameter) and self.start_width is not self.minor_axis_x:
                self.start_width.add_upper_dynamic(self.minor_axis_x, lambda x: x)
            if isinstance(self.start_width, ipars.FixedInstrumentParameter) and self.start_width is not self.minor_axis_x:
                if isinstance(self.minor_axis_x, ipars.RelativeFreeInstrumentParameter):
                    self.minor_axis_x.static_lower = self.start_width.get_value()

            if isinstance(self.end_width, ipars.RelativeFreeInstrumentParameter) and self.end_width is not self.minor_axis_x:
                self.end_width.add_upper_dynamic(self.minor_axis_x, lambda x: x)
            if isinstance(self.end_width, ipars.FixedInstrumentParameter) and self.end_width is not self.minor_axis_x:
                if isinstance(self.minor_axis_x, ipars.RelativeFreeInstrumentParameter):
                    self.minor_axis_x.static_lower = self.end_width.get_value()
        else:
            # Handle limits on minor_axis_x, which can't be less than start or end dimension
            if isinstance(self.minor_axis_x, ipars.RelativeFreeInstrumentParameter):
                self.minor_axis_x.add_dynamic_illegal_interval(self.start_width, lambda x: -x, lambda x: x)
                self.minor_axis_x.add_dynamic_illegal_interval(self.end_width, lambda x: -x, lambda x: x)


        # If a max_width is set, the start and end should have their limits reduced to this max
        if isinstance(self.start_width, ipars.RelativeFreeInstrumentParameter) and self.max_width is not None:
            self.start_width.static_upper = min([self.start_width.static_upper, self.max_width])

        if isinstance(self.end_width, ipars.RelativeFreeInstrumentParameter) and self.max_width is not None:
            self.end_width.static_upper = min([self.end_width.static_upper, self.max_width])
            """
            if not isinstance(self.end_width, ipars.RelativeFreeInstrumentParameter):
                if self.end_width.upper_bound > self.max_width:
                    self.end_width.upper_bound = self.max_width
            """

        if self.minor_axis_y_custom_parameter:
            # Attempt to set limits on start and end (except if the two parameters are the same)
            if isinstance(self.start_height, ipars.RelativeFreeInstrumentParameter) and self.start_height is not self.minor_axis_y:
                self.start_height.add_upper_dynamic(self.minor_axis_y, lambda x: x)
            if isinstance(self.start_height, ipars.FixedInstrumentParameter) and self.start_height is not self.minor_axis_y:
                if isinstance(self.minor_axis_y, ipars.RelativeFreeInstrumentParameter):
                    self.minor_axis_y.static_lower = self.start_height.get_value()

            if isinstance(self.end_height, ipars.RelativeFreeInstrumentParameter) and self.end_height is not self.minor_axis_y:
                self.end_height.add_upper_dynamic(self.minor_axis_y, lambda x: x)
            if isinstance(self.end_height, ipars.FixedInstrumentParameter) and self.end_height is not self.minor_axis_y:
                if isinstance(self.minor_axis_y, ipars.RelativeFreeInstrumentParameter):
                    self.minor_axis_y.static_lower = self.end_height.get_value()
        else:
            # Handle limits on minor_axis_y, which can't be less than start or end dimension
            if isinstance(self.minor_axis_y, ipars.RelativeFreeInstrumentParameter):
                self.minor_axis_y.add_dynamic_illegal_interval(self.start_height, lambda x: -x, lambda x: x)
                self.minor_axis_y.add_dynamic_illegal_interval(self.end_height, lambda x: -x, lambda x: x)

        # If a max_height is set, the start and end should have their limits reduced to this max
        if isinstance(self.start_height, ipars.RelativeFreeInstrumentParameter) and self.max_height is not None:
            self.start_height.static_upper = min([self.start_height.static_upper, self.max_height])
            """
            if not isinstance(self.start_height, ipars.RelativeFreeInstrumentParameter):
                if self.start_height.upper_bound > self.max_height:
                    self.start_height.upper_bound = self.max_height
            """

        if isinstance(self.end_height, ipars.RelativeFreeInstrumentParameter) and self.max_height is not None:
            self.end_height.static_upper = min([self.end_height.static_upper, self.max_height])
            """
            if not isinstance(self.end_height, ipars.RelativeFreeInstrumentParameter):
                if self.end_height.upper_bound > self.max_height:
                    self.end_height.upper_bound = self.max_height
            """

        # Need to add minor_axis_x and y to parameter pool
        self.current_parameters.add_parameter(self.minor_axis_x)
        self.current_parameters.add_parameter(self.minor_axis_y)

        # Instruct instrument to calculate length and get name
        length_name = self.get_length_name()

        instr = self.current_instrument

        # Calculate ellipse parameters in McStas instrument
        instr.add_declare_var("double", "tmp_w1")
        instr.add_declare_var("double", "tmp_w2")
        instr.append_initialize('')
        instr.append_initialize('tmp_w1=' + self.start_width.name + ';')
        instr.append_initialize('tmp_w2=' + self.end_width.name + ';')

        instr.add_declare_var("double", "tmp_b")
        instr.add_declare_var("double", "tmp_L")
        instr.append_initialize('tmp_b=fabs(0.5*' + self.minor_axis_x.name + ');')
        instr.append_initialize('tmp_L=' + length_name + ';')

        instr.add_declare_var("double", "tmp_k")
        instr.append_initialize('if (' + self.minor_axis_x.name + ' > 0) {')
        instr.append_initialize('tmp_k=cos(asin(tmp_w2/(2*tmp_b)))/cos(asin(tmp_w1/(2*tmp_b)));')
        instr.append_initialize('} else {')
        instr.append_initialize('tmp_k=cos(asin(tmp_w2/(2*tmp_b)))/cos(PI-asin(tmp_w1/(2*tmp_b)));')
        instr.append_initialize('}')

        instr.add_declare_var("double", "tmp_L1")
        instr.add_declare_var("double", "tmp_L2")
        instr.append_initialize('tmp_L1=tmp_L/(1+tmp_k);')
        instr.append_initialize('tmp_L2=tmp_L-tmp_L1;')

        instr.add_declare_var("double", "tmp_c")
        instr.append_initialize('if (' + self.minor_axis_x.name + ' > 0) {')
        instr.append_initialize('tmp_c=cos(asin(tmp_w1/(2*tmp_b)))*cos(asin(tmp_w1/(2*tmp_b)));')
        instr.append_initialize('} else {')
        instr.append_initialize('tmp_c=cos(PI-asin(tmp_w1/(2*tmp_b)))*cos(PI-asin(tmp_w1/(2*tmp_b)));')
        instr.append_initialize('}')

        Linx_par_name = self.name + "_Linx"
        Loutx_par_name = self.name + "_Loutx"
        instr.add_declare_var("double", Linx_par_name)
        instr.add_declare_var("double", Loutx_par_name)
        instr.append_initialize(Linx_par_name + '=-tmp_L1+sqrt(tmp_L1*tmp_L1*(1/tmp_c)-tmp_b*tmp_b);')
        instr.append_initialize(Loutx_par_name + '=' + Linx_par_name + '+tmp_L1-tmp_L2;')

        instr.append_initialize('')
        instr.add_declare_var("double", "tmp_h1")
        instr.add_declare_var("double", "tmp_h2")
        instr.append_initialize('tmp_h1=' + self.start_height.name + ';')
        instr.append_initialize('tmp_h2=' + self.end_height.name + ';')

        instr.append_initialize('tmp_b=fabs(0.5*' + self.minor_axis_y.name + ');')
        instr.append_initialize('tmp_L=' + length_name + ';')

        instr.append_initialize('if (' + self.minor_axis_y.name + ' > 0) {')
        instr.append_initialize('tmp_k=cos(asin(tmp_h2/(2*tmp_b)))/cos(asin(tmp_h1/(2*tmp_b)));')
        instr.append_initialize('} else {')
        instr.append_initialize('tmp_k=cos( asin(tmp_h2/(2*tmp_b)))/cos(PI-asin(tmp_h1/(2*tmp_b)));')
        instr.append_initialize('}')

        instr.append_initialize('tmp_L1=tmp_L/(1+tmp_k);')
        instr.append_initialize('tmp_L2=tmp_L-tmp_L1;')

        instr.append_initialize('if (' + self.minor_axis_y.name + ' > 0) {')
        instr.append_initialize('tmp_c=cos(asin(tmp_h1/(2*tmp_b)))*cos(asin(tmp_h1/(2*tmp_b)));')
        instr.append_initialize('} else {')
        instr.append_initialize('tmp_c=cos(PI-asin(tmp_h1/(2*tmp_b)))*cos(PI-asin(tmp_h1/(2*tmp_b)));')
        instr.append_initialize('}')

        Liny_par_name = self.name + "_Liny"
        Louty_par_name = self.name + "_Louty"
        instr.add_declare_var("double", Liny_par_name)
        instr.add_declare_var("double", Louty_par_name)
        instr.append_initialize(Liny_par_name + '=-tmp_L1+sqrt(tmp_L1*tmp_L1*(1/tmp_c)-tmp_b*tmp_b);')
        instr.append_initialize(Louty_par_name + '=' + Liny_par_name + '+tmp_L1-tmp_L2;')

        # Add the guide component and use the calculated variables for its properties
        guide = self.current_instrument.add_component(self.name, "Elliptic_guide_gravity")
        guide.set_AT([0, 0, 0], RELATIVE=self.reference_component_name)

        guide.l = length_name + " - 1E-6"

        guide.linxw = Linx_par_name
        guide.loutxw = Loutx_par_name
        guide.linyh = Liny_par_name
        guide.loutyh = Louty_par_name

        guide.dimensionsAt = '"mid"'
        guide.xwidth = "fabs(" + self.minor_axis_x.name + ")"
        guide.yheight = "fabs(" + self.minor_axis_y.name + ")"

        # Temporary reflectivity model
        guide.R0 = self.R0
        guide.m = self.m
        guide.Qc = self.Qc
        guide.alpha = self.alpha
        guide.W = self.W
        guide.enableGravity = self.enableGravity

        end = self.current_instrument.add_component(self.end_component_name, "Arm")
        end.set_AT([0, 0, self.get_length_name()], RELATIVE=guide)

import numpy as np


def ellipse_calculation(ellipse_pos, start, end, start_dim, end_dim, minor_axis):

    abs_minor_axis = abs(minor_axis)
    abs_half_minor_axis = abs(0.5 * minor_axis)

    arcsin_argument = end_dim / (2 * abs_half_minor_axis)
    if arcsin_argument >= 1 or arcsin_argument <= -1:
        print("arcsin error, end and half axis")
        print("end", end_dim, "minor_axis", minor_axis)
        print("arcsin_argument", arcsin_argument)

    arcsin_argument = start_dim / (2 * abs_half_minor_axis)
    if arcsin_argument >= 1 or arcsin_argument <= -1:
        print("arcsin error, end and half axis")
        print("start", start_dim, "minor_axis", minor_axis)
        print("arcsin_argument", arcsin_argument)

    element_length = end - start
    if minor_axis > 0:
        tmp_k = np.cos(np.arcsin(end_dim / (2 * abs_half_minor_axis))) / np.cos(
            np.arcsin(start_dim / (2 * abs_half_minor_axis)))
    else:
        tmp_k = np.cos(np.arcsin(end_dim / (2 * abs_half_minor_axis))) / np.cos(
            np.pi - np.arcsin(start_dim / (2 * abs_half_minor_axis)))

    focal_before = element_length / (1 + tmp_k)
    focal_after = element_length - focal_before

    if minor_axis > 0:
        tmp_c = np.cos(np.arcsin(start_dim / (2 * abs_half_minor_axis))) * np.cos(
            np.arcsin(start_dim / (2 * abs_half_minor_axis)))
    else:
        tmp_c = np.cos(np.pi - np.arcsin(start_dim / (2 * abs_half_minor_axis))) * np.cos(
            np.pi - np.arcsin(start_dim / (2 * abs_half_minor_axis)))

    focus_L_in = -focal_before + np.sqrt(
        focal_before * focal_before * (1 / tmp_c) - abs_half_minor_axis * abs_half_minor_axis)
    focus_L_out = focus_L_in + focal_before - focal_after

    focus_s = - focus_L_in
    focus_e = element_length + focus_L_out
    e_length = focus_e - focus_s

    ellipse_p_side = abs_half_minor_axis * np.sqrt(1 - (((ellipse_pos - focus_s) - e_length / 2) / (e_length / 2)) * (
                ((ellipse_pos - focus_s) - e_length / 2) / (e_length / 2)))
    ellipse_n_side = - abs_half_minor_axis * np.sqrt(1 - (((ellipse_pos - focus_s) - e_length / 2) / (e_length / 2)) * (
                ((ellipse_pos - focus_s) - e_length / 2) / (e_length / 2)))

    return ellipse_p_side, ellipse_n_side

def plot_element_horizontal(ax, par_dict, color):

    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_width = par_dict["start_width"]
    end_width = par_dict["end_width"]
    minor_axis = par_dict["minor_axis_x"]

    ellipse_pos = np.linspace(0, end - start, 100)
    ellipse_p_side, ellipse_n_side = ellipse_calculation(ellipse_pos, start, end, start_width, end_width, minor_axis)

    ax.plot(start + ellipse_pos, ellipse_p_side, color=color)
    ax.plot(start + ellipse_pos, ellipse_n_side, color=color)


def plot_element_vertical(ax, par_dict, color):

    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_height = par_dict["start_height"]
    end_height = par_dict["end_height"]
    minor_axis = par_dict["minor_axis_y"]

    ellipse_pos = np.linspace(0, end - start, 100)
    ellipse_p_side, ellipse_n_side = ellipse_calculation(ellipse_pos, start, end, start_height, end_height, minor_axis)

    ax.plot(start + ellipse_pos, ellipse_p_side, color=color)
    ax.plot(start + ellipse_pos, ellipse_n_side, color=color)

def guide_width(par_dict, distance_unitless):
    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_width = par_dict["start_width"]
    end_width = par_dict["end_width"]
    minor_axis = par_dict["minor_axis_x"]

    ellipse_pos = (end-start)*distance_unitless
    ellipse_p_side, ellipse_n_side = ellipse_calculation(ellipse_pos, start, end, start_width, end_width, minor_axis)
    return 2.0 * ellipse_p_side

def guide_height(par_dict, distance_unitless):
    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_height = par_dict["start_height"]
    end_height = par_dict["end_height"]
    minor_axis = par_dict["minor_axis_y"]

    ellipse_pos = (end-start)*distance_unitless
    ellipse_p_side, ellipse_n_side = ellipse_calculation(ellipse_pos, start, end, start_height, end_height, minor_axis)
    return 2.0 * ellipse_p_side

def guide_dimensions(par_dict, distance_unitless, horizontal):
    start = par_dict["start_point"]
    end = par_dict["next_start_point"]

    if horizontal:
        start_dim = par_dict["start_width"]
        end_dim = par_dict["end_width"]
        minor_axis = par_dict["minor_axis_x"]
    else:
        start_dim = par_dict["start_height"]
        end_dim = par_dict["end_height"]
        minor_axis = par_dict["minor_axis_y"]

    ellipse_pos = (end - start) * distance_unitless
    ellipse_p_side, ellipse_n_side = ellipse_calculation(ellipse_pos, start, end, start_dim, end_dim, minor_axis)
    return 2.0 * ellipse_p_side


def center_line(start_pr, par_dict, distance_unit_less):

    start = par_dict["start_point"]
    end = par_dict["next_start_point"]

    length = end - start
    this_position = length*distance_unit_less

    z_vector = np.array([0, 0, 1])
    start_direction = start_pr.rotation
    z_vector = start_direction.apply(z_vector)

    updated_position = start_pr.position + this_position*z_vector

    return PositionAndRotation(updated_position, start_pr.rotation)