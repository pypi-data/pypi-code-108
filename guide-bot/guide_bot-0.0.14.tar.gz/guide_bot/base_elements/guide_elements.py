import os
import shutil

import numpy as np

from guide_bot.parameters import instrument_parameters as ipars


def handle_input_parameter(name, par, default_min=None, default_max=None):
    """
    Handles input parameters given to elements and returns InstrumentParameter

    Any parameter to be optimized by elements can be given as keyword
    arguments when they are initialized, and these conform to the following
    logic:

    If the parameter keyword is not used, it will be optimized within default
    limits.

    If a list of length two is given, it will be optimized and the values will
    be used as limits (each limit can be None).

    If a value is specified (float/int), the parameter is fixed to that value.

    Alternatively, the user can provide the InstrumentParameter object
    directly, which will then be returned. In case a DependentInstrumentObject
    is given, it will be checked if it can be calculated, and in that case
    it will be converted to a fixed parameter. If they depend on a free
    parameter, they can not be calculated before each optimization step.

    Parameters
    ----------
    name : (str)
        Name of the parameter (will later be extended)

    par : (float, None, InstrumentParameter)
        Parameter information given to the element

    default_min : float
        Default minimum value for this parameter

    default_max : float
        Default maximum value for this parameter

    Returns
    -------

    par : (FreeInstrumentParamter, FixedInstrumentParameter,
           DependentInstrumentParamter)
        The returned InstrumentParameter object
    """
    # If the user is already providing a parameter, use that directly
    if isinstance(par, (ipars.FixedInstrumentParameter, ipars.FreeInstrumentParameter)):
        return par

    if isinstance(par, ipars.DependentInstrumentParameter):
        # Check if any dependents are free
        if par.depends_on_free():
            return par
        else:
            # if no free dependents, convert to a FixedInstrumentParameter
            par.calculate()
            value = par.get_value()
            return ipars.FixedInstrumentParameter(par.name, value)

    if par is not None:
        if isinstance(par, list):
            # List can only be when a range is set for a free parameter
            if len(par) != 2:
                raise ValueError("When setting min, max with list, it must have length 2.")

            min_value = par[0]
            max_value = par[1]

            return ipars.RelativeFreeInstrumentParameter(name, min_value, max_value)

        else:
            # Assume a fixed value is given
            if not isinstance(par, (int, float)):
                raise ValueError("When setting a parameter value, it should be a float or integer.")

            return ipars.FixedInstrumentParameter(name, par)
    
    else:
        # If nothing is specified, use default range (can both be None, None for length / start_point)
        return ipars.RelativeFreeInstrumentParameter(name, default_min, default_max)


class Element:
    """
    Base class for a element that could be part of a guide.

    Each element will have a length and a start point which is a distance
    from the source. These can be optimized or specified.

    Currently, length and start_point can not be DependentInstrumentParameters
    """
    def __init__(self, name, length=None, start_point=None, **kwargs):
        """
        Initialize a guide element with name and optional length / start_point

        Creates attributes for start_point parameter and
        next_start_point_parameter which is used by the length system to set
        the necessary free parameters for satisfying the total length
        constraint.

        May have an owner specified to differentiate between elements added by
        the user, moderator and sample.

        Parameters
        ----------

        name : (str)
            Name of the guide element

        length : (float, None, InstrumentParameter)
            Length of guide element, optimized parameter

        start_point : (float, None, InstrumentParameter)
            Distance from source to start of the guide element
        """

        self.name = name

        if isinstance(length, ipars.InstrumentParameter):
            raise ValueError("length parameter not allowed to be custom parameter.")

        if isinstance(start_point, ipars.InstrumentParameter):
            raise ValueError("start_point parameter not allowed to be custom parameter.")

        self.length = handle_input_parameter(name + "_length", length)
        self.start_point = handle_input_parameter(name + "_start_point", start_point)
        
        self.start_point_parameter = None
        self.next_start_point_parameter = None

        self.reference_component_name = None
        self.end_component_name = name + "_end_point"

        self.owner = None

    def set_owner(self, owner):
        """
        Sets the owner of this Element

        Parameters
        ----------

        owner : str
            Specifies the owner of this Element
        """

        self.owner = owner

    def __repr__(self):
        """
        Provides a basic description of the guide element

        """
        string = "Element: "

        string += self.name + " : \n"
        string += self.length.__repr__() + "\n"
        string += self.start_point.__repr__()

        return string


class GuideElement(Element):
    """
    Element of a guide, including width / height at start. It is assumed it
    will connect to the next element, and thus width / height of end is
    determined by the next guide element. For this reason, a gap in the guide
    is still considered a GuideElement, for example for a chopper.

    """
    def __init__(self, name, length=None, start_point=None, start_width=None, start_height=None,
                 end_width=None, end_height=None, **kwargs):
        """
        Initializing a GuideElement that can be part of a guide

        A GuideElement has length, a start_point, which is the distance from
        source to the start of the guide, and a start width/height. The
        entrance dimensions are typically optimized, and need a default range.

        Initialized GuideElements are provided by the user and is thus an
        important part of the user interface.

        The exit dimensions are determined by the next element, and a parameter
        for this purpose is assigned to these atributes.

        The current_instrument and current_parameters are internalized, allowing
        classes that inherit from GuideElement to easily add new parameters and
        expand the McStas instrument.

        Parameters
        ----------
        name : (str)
            Name of the guide element

        length : (float, int, None, InstrumentParameter)
            Length of guide element, optimized parameter

        start_point : (float, int, None, InstrumentParameter)
            Distance from source to start of the guide element

        start_width : (float, int, None, InstrumentParameter)
            Width of guide entrance

        start_height : (float, int, None, InstrumentParameter)
            Height of guide entrance

        """
        # Maybe it should be up to the GuideElement if they want the user to set start_width/height?
        # Want to be able to make straight modules that just set start_width to end_width
        # These could derive directly from Element instead, but would then have to add a few things
        # A few solutions
        #  A) Have another class between Element and GuideElement that adds all but start_width/height
        #  B) Provide a easy function to set start_width / height (already kind of the case) and have childen do that
        #  C) Move a few things to Element, what element can exists without current_instr / pars?
        #  D) Remove the start_width / height from the parameter pool by overwriting setup_instr_and_pars
        #
        # Still need to ensure all elements have a start_width / height.

        self.start_width = handle_input_parameter(name + "_start_width", start_width,
                                                  default_min=0.005, default_max=0.15)

        self.start_height = handle_input_parameter(name + "_start_height", start_height,
                                                   default_min=0.005, default_max=0.15)

        if end_width is None:
            self.end_width = None
        else:
            self.end_width = handle_input_parameter(name + "_end_width", end_width,
                                                    default_min=0.005, default_max=0.15)

        if end_height is None:
            self.end_height = None
        else:
            self.end_height = handle_input_parameter(name + "_end_height", end_height,
                                                     default_min=0.005, default_max=0.15)

        self.current_instrument = None
        self.current_parameters = None

        super().__init__(name, length=length, start_point=start_point, **kwargs)
    
    def setup_instrument_and_parameters(self, instrument, instrument_parameters):
        """
        Set current_instrument and current_parameters attributes using the
        defined instrument and instrument parameters for a certain run among
        many. Adds start_width / height to the current_parameter object,
        which is a container for all parameters of the instrument.
        """
        self.current_instrument = instrument
        self.current_parameters = instrument_parameters
    
        self.current_parameters.add_parameter(self.start_width)
        self.current_parameters.add_parameter(self.start_height)

    def create_new_parameter(self, *args, **kwargs):
        """
        Uncertain about the need for this method

        Add new parameter on the form:
            Fixed parameter: name, value
            Free parameter: name, value, min, max
            Dependent parameter: name, dependent_on, function, constants
        """
    
        if self.current_instrument is None:
            raise ValueError("No instrument object set yet!")

        if self.current_parameters is None:
            raise ValueError("No parameter object set yet!")

        variable_name = args[0]
        
        #self.current_instrument.add_parameter(variable_name)

        if "dependent_on" in kwargs and "func" in kwargs:
            if "constants" in kwargs:
                constants = kwargs["constants"]
            else:
                constants = []
            par = ipars.DependentInstrumentParameter(variable_name, dependent_on=kwargs["dependent_on"],
                                                     func=kwargs["func"], constants=constants)
        elif len(args) == 2:
            par = ipars.FixedInstrumentParameter(variable_name, args[1])
        elif len(args) == 3:
            par = ipars.FreeInstrumentParameter(variable_name, args[1], args[2])

        self.current_parameters.add_parameter(par)
        
        return par

    def set_end_dimensions(self, end_width, end_height):
        """
        Sets the end_width / height attributes, these have a type derived
        from InstrumentParameter.
        """

        self.end_width = end_width
        self.end_height = end_height
    
    def get_length_name(self):
        """
        Provides length name, ensures this variable is available in instrument

        When adding components describing the GuideElement to the instrument
        file, the length will most probably be needed. This method adds code
        to the instrument file that declares a length variable and calculates
        it from the change points that is used as instrument inputs. It then
        returns the name of the variable, which can be used when setting up
        the McStas components.
        """

        # This can go into a method somewhere, very normal operation
        previous_cb_name = self.start_point_parameter.name
        next_cb_name = self.next_start_point_parameter.name
        length_var_name = self.name + "_length"
        self.current_instrument.add_declare_var("double", length_var_name)
        self.current_instrument.append_initialize(length_var_name + " = " + next_cb_name + " - " + previous_cb_name + ";")
        
        self.length_parameter = length_var_name
    
        return length_var_name

    def calculate_length(self):
        self.element_length = self.next_start_point_parameter.get_value() - self.start_point_parameter.get_value()

    def write_to_log_base(self, file):
        """
        Base method for writing basic information to guide log file, not to be overwritten
        """

        file.write("\nElement " + self.__class__.__name__ + " " + self.name + "\n")
        self.write_parameter(file, "start_point", self.start_point_parameter, "start_point")
        self.write_parameter(file, "next_start_point", self.next_start_point_parameter, "start_point")
        self.write_parameter(file, "start_width", self.start_width, "horizontal")
        self.write_parameter(file, "start_height", self.start_height, "vertical")
        self.write_parameter(file, "end_width", self.end_width, "horizontal")
        self.write_parameter(file, "end_height", self.end_height, "vertical")

    def write_parameter(self, file, log_name, parameter, type_string=None):
        """
        Method for writing to log file in order to keep consistency and do error checks
        """
        if type_string not in ("horizontal", "vertical", "start_point", None):
            raise RuntimeError("type_string needs to be horizontal, vertical, start_point or None")

        if type_string is None:
            type_string = ""

        file.write(" " + log_name.ljust(29) + type_string.ljust(15) + parameter.name.ljust(50) + "\n")

    def write_to_log(self, file):
        """
        Template function which should be overwritten for guide elements to add more details as necessary
        """

        self.write_to_log_base(file)

    def copy_component(self, name, destination):
        this_file_path = os.path.abspath(__file__)
        this_directory = os.path.split(this_file_path)[0]
        component_path = os.path.join(this_directory, "..", "..", "McStas_components", name)
        destination_path = os.path.join(destination, name)

        shutil.copyfile(component_path, destination_path)

    def copy_components(self, destination):
        return []

    def __repr__(self):
        """
        Provides a basic description of the guide element
        """

        name_length = 12
        string = "GuideElement: "

        string += self.name + " : \n"
        string += "length:".ljust(name_length) + self.length.__repr__() + "\n"
        string += "start:".ljust(name_length) + self.start_point.__repr__() + "\n"
        string += "s width:".ljust(name_length) + self.start_width.__repr__() + "\n"
        string += "s height:".ljust(name_length) + self.start_height.__repr__() + "\n"
        if self.end_width is not None:
            string += "e width:".ljust(name_length) + self.end_width.__repr__() + "\n"
        else:
            string += "no end_width set\n"
        if self.end_height is not None:
            string += "e height:".ljust(name_length) + self.end_height.__repr__() + "\n"
        else:
            string += "no end_height set\n"

        string += "start par:".ljust(name_length) + self.start_point_parameter.__repr__() + "\n"
        string += "n start p:".ljust(name_length) + self.next_start_point_parameter.__repr__()

        return string


class PositionAndRotation:
    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation

    def width_points(self, width):

        x_vector = np.array([0.5, 0, 0])
        x_vector = self.rotation.apply(x_vector)

        m_position = self.position - width * x_vector
        p_position = self.position + width * x_vector

        return m_position, p_position

    def height_points(self, height):

        y_vector = np.array([0, 0.5, 0])
        y_vector = self.rotation.apply(y_vector)

        m_position = self.position - height * y_vector
        p_position = self.position + height * y_vector

        return m_position, p_position

    def get_points(self, distance, horizontal):
        """
        Provides 3D points for plotting

        Takes distance between points and wether it is in the
        horizontal direction or vertical (True / False).

        distance: float
            distance between points

        horizontal: bool
            are they spaced horizontally or vertically
        """
        if horizontal:
            return self.width_points(distance)
        else:
            return self.height_points(distance)

    def __repr__(self):
        string = "PositionAndRotation\n"
        string += " Position: " + str(self.position) + "\n"
        string += " Rotation: \n" + str(self.rotation.as_matrix()) + "\n"

        return string