import numpy as np

from scipy.spatial.transform import Rotation as R

from guide_bot.base_elements import guide_elements
from guide_bot.base_elements.guide_elements import PositionAndRotation
from guide_bot.parameters import instrument_parameters as ipars


class Curved(guide_elements.GuideElement):
    """
    Curved GuideElement that inserts a curved section into a guide

    A curved guide section with equal start and end dimensions,
    meaning it has a constant cross section.
    """

    def __init__(self, name, length=None, start_point=None,
                 start_width=None, start_height=None,
                 angle=None, bend="left",
                 **kwargs):
        """
        Curved GuideElement that inserts a curved section into a guide

        A curved guide section with equal start and end dimensions,
        meaning it has a constant cross section.

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
        """
        # Internalize stuff relevant for this Element

        super().__init__(name, length=length, start_point=start_point,
                         start_width=start_width, start_height=start_height,
                         end_width=None, end_height=None,
                         **kwargs)

        # This McStas component only supports constant cross section
        self.end_width = self.start_width
        self.end_height = self.start_height

        if bend == "left":
            self.horizontal_bend = True
            self.positive_bend = True

            self.horizontal_bend_par = ipars.FixedInstrumentParameter(self.name + "_horizontal", 1)
            self.positive_bend_par = ipars.FixedInstrumentParameter(self.name + "_bend_dir", 1)
        elif bend == "right":
            self.horizontal_bend = True
            self.positive_bend = False

            self.horizontal_bend_par = ipars.FixedInstrumentParameter(self.name + "_horizontal", 1)
            self.positive_bend_par = ipars.FixedInstrumentParameter(self.name + "_bend_dir", -1)
        elif bend == "down":
            self.horizontal_bend = False
            self.positive_bend = False

            self.horizontal_bend_par = ipars.FixedInstrumentParameter(self.name + "_horizontal", -1)
            self.positive_bend_par = ipars.FixedInstrumentParameter(self.name + "_bend_dir", -1)
        elif bend == "up":
            self.horizontal_bend = False
            self.positive_bend = True

            self.horizontal_bend_par = ipars.FixedInstrumentParameter(self.name + "_horizontal", -1)
            self.positive_bend_par = ipars.FixedInstrumentParameter(self.name + "_bend_dir", 1)
        else:
            raise ValueError("bend must be left, right, up or down (string).")

        # How to handle a los parameter?
        if angle is None:
            # automatic los, not made yet
            raise ValueError("Need to specify angular_diversion")
        else:
            if isinstance(angle, ipars.FreeInstrumentParameter):
                raise ValueError("Not supported to have angular_diversion as a free parameter")
            elif isinstance(angle, ipars.InstrumentParameter):
                # Fixed or dependent
                self.angular_diversion = angle
            elif isinstance(angle, (float, int)):
                self.angular_diversion = ipars.FixedInstrumentParameter(self.name + "_angular_diversion", angle)
            else:
                raise ValueError("Unknown type of angular_diversion")

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

    def copy_components(self, destination):
        components_to_copy = ["Guide_curved_gravity_safe.comp"]

        self.copy_component(components_to_copy[0], destination)

        return components_to_copy

    def add_to_instr(self):
        """
        Adds code describing the straight element to the current McStas instrument

        This methods uses McStasScript to add components and code to a McStas
        instrument object. The McStas instrument object is an attribute of the
        class called current_instrument. New instrument parameters can also be
        created and added to the optimization by using the current_parameters
        attribute.

        Since the add_to_instr method of all the Elements are called in order
        from the sample to the source, it is important the components are
        added after the Origin component to ensure the correct order.
        """

        self.current_parameters.add_parameter(self.angular_diversion)
        self.current_parameters.add_parameter(self.horizontal_bend_par)
        self.current_parameters.add_parameter(self.positive_bend_par)

        # Calculate curvature
        curvature_name = self.name + "_curvature"
        self.current_instrument.add_declare_var("double", curvature_name)

        curvature_calc = curvature_name + " = " + self.get_length_name() + "/" + self.angular_diversion.name + ";"
        self.current_instrument.append_initialize(curvature_calc)

        # Calculating end point of curved guide
        end_x_par_name = self.name + "_end_X"
        end_y_par_name = self.name + "_end_Y"
        end_z_par_name = self.name + "_end_Z"
        self.current_instrument.add_declare_var("double", end_x_par_name)
        self.current_instrument.add_declare_var("double", end_y_par_name)
        self.current_instrument.add_declare_var("double", end_z_par_name)

        if self.horizontal_bend and self.positive_bend:
            guide_z_rot = 0
            end_rot = [0, self.angular_diversion.name + "*RAD2DEG", 0]

            initialize_line1 = end_x_par_name + " = " + curvature_name + "*(1-cos(" + self.angular_diversion.name + "));"
            initialize_line2 = end_y_par_name + " = 0;"
            initialize_line3 = end_z_par_name + " = " + curvature_name + "*sin(" + self.angular_diversion.name + ");"

        elif self.horizontal_bend and not self.positive_bend:
            guide_z_rot = 180
            end_rot = [0, "-" + self.angular_diversion.name + "*RAD2DEG", 0]

            initialize_line1 = end_x_par_name + " = -" + curvature_name + "*(1-cos(" + self.angular_diversion.name + "));"
            initialize_line2 = end_y_par_name + " = 0;"
            initialize_line3 = end_z_par_name + " = " + curvature_name + "*sin(" + self.angular_diversion.name + ");"

        elif not self.horizontal_bend and self.positive_bend:
            guide_z_rot = 90
            end_rot = ["-" + self.angular_diversion.name + "*RAD2DEG", 0, 0]

            initialize_line1 = end_x_par_name + " = 0;"
            initialize_line2 = end_y_par_name + " = " + curvature_name + "*(1-cos(" + self.angular_diversion.name + "));"
            initialize_line3 = end_z_par_name + " = " + curvature_name + "*sin(" + self.angular_diversion.name + ");"

        elif not self.horizontal_bend and not self.positive_bend:
            guide_z_rot = 270
            end_rot = [self.angular_diversion.name + "*RAD2DEG", 0, 0]

            initialize_line1 = end_x_par_name + " = 0;"
            initialize_line2 = end_y_par_name + " = -" + curvature_name + "*(1-cos(" + self.angular_diversion.name + "));"
            initialize_line3 = end_z_par_name + " = " + curvature_name + "*sin(" + self.angular_diversion.name + ");"

        self.current_instrument.append_initialize(initialize_line1)
        self.current_instrument.append_initialize(initialize_line2)
        self.current_instrument.append_initialize(initialize_line3)

        guide = self.current_instrument.add_component(self.name, "Guide_curved_gravity_safe")
        guide.set_AT([0, 0, 0], RELATIVE=self.reference_component_name)
        guide.set_ROTATED([0, 0, guide_z_rot], RELATIVE=self.reference_component_name)

        # turning the guide to vertical direction switches horizontal and vertical.
        if self.horizontal_bend:
            guide.w1 = self.start_width.name
            guide.h1 = self.start_height.name
        else:
            guide.w1 = self.start_height.name
            guide.h1 = self.start_width.name

        guide.l = self.get_length_name()
        guide.curvature = curvature_name

        # Temporary reflectivity model
        guide.R0 = self.R0
        guide.m = self.m
        guide.Qc = self.Qc
        guide.alpha = self.alpha
        guide.W = self.W

        end_arm = self.current_instrument.add_component(self.end_component_name, "Arm")
        end_arm.set_AT([end_x_par_name, end_y_par_name, end_z_par_name], RELATIVE=self.reference_component_name)
        end_arm.set_ROTATED(end_rot, RELATIVE=self.reference_component_name)

    def write_to_log(self, file):
        self.write_to_log_base(file)
        if self.horizontal_bend:
            direction = "horizontal"
        else:
            direction = "vertical"

        self.write_parameter(file, "angular_diversion", self.angular_diversion, direction)
        self.write_parameter(file, "bend_horizontal", self.horizontal_bend_par, direction)
        self.write_parameter(file, "bend_direction", self.positive_bend_par, direction)


def plot_element_horizontal(ax, par_dict, color):
    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_width = par_dict["start_width"]
    end_width = par_dict["end_width"]

    ax.plot([start, end], [0.5 * start_width, 0.5 * end_width], color=color)
    ax.plot([start, end], [-0.5 * start_width, -0.5 * end_width], color=color)


def plot_element_vertical(ax, par_dict, color):
    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_height = par_dict["start_height"]
    end_height = par_dict["end_height"]

    ax.plot([start, end], [0.5 * start_height, 0.5 * end_height], color=color)
    ax.plot([start, end], [-0.5 * start_height, -0.5 * end_height], color=color)


def guide_width(par_dict, distance_unit_less):
    return par_dict["start_width"]


def guide_height(par_dict, distance_unit_less):
    return par_dict["start_height"]

def guide_dimensions(par_dict, distance_unitless, horizontal):
    if horizontal:
        return par_dict["start_width"]
    else:
        return par_dict["start_height"]


def center_line(start_pr, par_dict, distance_unit_less):

    angular_diversion = par_dict["angular_diversion"]
    bend_horizontal = par_dict["bend_horizontal"]
    bend_direction = par_dict["bend_direction"]

    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_height = par_dict["start_height"]
    end_height = par_dict["end_height"]

    length = end - start
    curvature = length/angular_diversion

    rotation = distance_unit_less*angular_diversion

    displacement = bend_direction*curvature*(1-np.cos(rotation))
    if bend_horizontal == 1:
        displacement_x = displacement
        displacement_y = 0
    elif bend_horizontal == -1:
        displacement_x = 0
        displacement_y = displacement

    displacement_z = curvature*np.sin(rotation)

    x_vector = np.array([1, 0, 0])
    y_vector = np.array([0, 1, 0])
    z_vector = np.array([0, 0, 1])

    start_direction = start_pr.rotation

    x_vector = start_direction.apply(x_vector)
    y_vector = start_direction.apply(y_vector)
    z_vector = start_direction.apply(z_vector)

    updated_position = start_pr.position + displacement_x*x_vector + displacement_y*y_vector + displacement_z*z_vector
    if bend_horizontal == 1:
        updated_rotation = start_pr.rotation * R.from_euler("y", bend_direction * rotation)
    elif bend_horizontal == -1:
        updated_rotation = start_pr.rotation * R.from_euler("x", -bend_direction * rotation)

    return PositionAndRotation(updated_position, updated_rotation)






