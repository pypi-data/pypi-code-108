import numpy as np
from guide_bot.base_elements import guide_elements
from guide_bot.base_elements.guide_elements import PositionAndRotation


class Straight(guide_elements.GuideElement):
    """
    Straight GuideElement that inserts a guide with flat mirrors into a guide

    A straight guide section with independent start and end dimensions,
    meaning it can have sloping mirrors, but they are flat. If end_width
    or end_height is specified, they will override the  start_width or
    start_height setting of the next Element in the guide.
    """
    def __init__(self, name, length=None, start_point=None,
                 start_width=None, start_height=None,
                 end_width=None, end_height=None, **kwargs):
        """
        Straight GuideElement that inserts a guide with flat mirrors into a guide

        A straight guide section with independent start and end dimensions,
        meaning it can have sloping mirrors, but they are flat. If end_width
        or end_height is specified, they will override the  start_width or
        start_height setting of the next Element in the guide.

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
                         end_width=end_width, end_height=end_height,
                         **kwargs)

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

        guide = self.current_instrument.add_component(self.name, "Guide_gravity")
        guide.set_AT([0, 0, 0], RELATIVE=self.reference_component_name)
        
        guide.w1 = self.start_width.name
        guide.h1 = self.start_height.name

        guide.w2 = self.end_width.name
        guide.h2 = self.end_height.name

        guide.l = self.get_length_name() + " - 1E-6"

        # Temporary reflectivity model
        guide.R0 = self.R0
        guide.m = self.m
        guide.Qc = self.Qc
        guide.alpha = self.alpha
        guide.W = self.W

        end = self.current_instrument.add_component(self.end_component_name, "Arm")
        end.set_AT([0, 0, self.get_length_name()], RELATIVE=guide)


def plot_element_horizontal(ax, par_dict, color):

    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_width = par_dict["start_width"]
    end_width = par_dict["end_width"]

    ax.plot([start, end], [0.5*start_width, 0.5*end_width], color=color)
    ax.plot([start, end], [-0.5*start_width, -0.5*end_width], color=color)


def plot_element_vertical(ax, par_dict, color):

    start = par_dict["start_point"]
    end = par_dict["next_start_point"]
    start_height = par_dict["start_height"]
    end_height = par_dict["end_height"]

    ax.plot([start, end], [0.5*start_height, 0.5*end_height], color=color)
    ax.plot([start, end], [-0.5*start_height, -0.5*end_height], color=color)


def guide_width(par_dict, distance_unit_less):
    start_width = par_dict["start_width"]
    end_width = par_dict["end_width"]

    return start_width + (end_width - start_width) * distance_unit_less


def guide_height(par_dict, distance_unit_less):
    start_height = par_dict["start_height"]
    end_height = par_dict["end_height"]

    return start_height + (end_height - start_height)*distance_unit_less


def guide_dimensions(par_dict, distance_unitless, horizontal):

    if horizontal:
        start_width = par_dict["start_width"]
        end_width = par_dict["end_width"]

        return start_width + (end_width - start_width) * distance_unitless

    else:
        start_height = par_dict["start_height"]
        end_height = par_dict["end_height"]

        return start_height + (end_height - start_height) * distance_unitless


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