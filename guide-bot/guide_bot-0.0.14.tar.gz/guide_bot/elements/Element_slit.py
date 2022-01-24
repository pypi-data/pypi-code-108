from guide_bot.base_elements import guide_elements

class Slit(guide_elements.GuideElement):
    """
    Gap GuideElement that inserts an empty space into a guide

    A Gap still has start and end dimensions as it is supposed to fit with the
    surrounding elements, as if it was a guide element. In this way, it can
    for example be used to set a gap for a chopper, and force the adjacent
    Elements to narrow to the required width / height for the chopper.
    """

    def __init__(self, name, length=None, start_point=None,
                 start_width=None, start_height=None,
                 end_width=None, end_height=None, **kwargs):
        """
        Slit GuideElement that inserts an empty space into a guide preceeded by a slit

        A Slit still has start and end dimensions as it is supposed to fit with
        the surrounding elements, as if it was a guide element. In this way,
        it can for example be used to set a gap for a chopper, and force the
        adjacent Elements to narrow to the required width / height for the
        chopper. If end_width / end_height is specified, they will override
        the following modules start_width / start_height settings.

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
        
        # Internalize stuff relevant for this
        
        super().__init__(name, length=length, start_point=start_point,
                         start_width=start_width, start_height=start_height,
                         end_width=end_width, end_height=end_height, **kwargs)

    def add_to_instr(self):
        """
        Adds code describing the gap element to the current McStas instrument

        This methods uses McStasScript to add components and code to a McStas
        instrument object. The McStas instrument object is an attribute of the
        class called current_instrument. New instrument parameters can also be
        created and added to the optimization by using the current_parameters
        attribute.

        Since the add_to_instr method of all the Elements are called in order
        from the sample to the source, it is important the components are
        added after the Origin component to ensure the correct order.
        """

        slit = self.current_instrument.add_component(self.name, "Slit")
        slit.set_AT([0, 0, 0], RELATIVE=self.reference_component_name)
        slit.xwidth = self.start_width.name
        slit.yheight = self.start_height.name

        end = self.current_instrument.add_component(self.end_component_name, "Arm")
        end.set_AT([0, 0, self.get_length_name()], RELATIVE=slit)

def plot_element_horizontal(ax, par_dict, color):
    start = par_dict["start_point"]
    start_width = par_dict["start_width"]

    ax.plot([start, start], [0.5*start_width,  0.75*start_width], color=color)
    ax.plot([start, start], [-0.5*start_width, -0.75*start_width], color=color)

def plot_element_vertical(ax, par_dict, color):
    start = par_dict["start_point"]
    start_height = par_dict["start_height"]

    ax.plot([start, start], [0.5 * start_height, 0.75 * start_height], color=color)
    ax.plot([start, start], [-0.5 * start_height, -0.75 * start_height], color=color)

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