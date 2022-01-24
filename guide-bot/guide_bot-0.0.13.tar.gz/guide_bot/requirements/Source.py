
from guide_bot.requirements.requirement_parameters import Parameters
from guide_bot.parameters import instrument_parameters as ipars
from guide_bot.base_elements.guide_elements import GuideElement
from guide_bot.elements import Element_gap
from mcstasscript.interface import instr, plotter, functions
import math
import numpy as np


class BaseSource:
    """
    Base class for a source used in optimization / characterization of a guide

    The BaseSource class is meant as a base class from which other classes can
    inherit the central features required for a source in guide_bot. It
    provides the basic parameters that is expected of every source, the logic
    for deciding distance from source to guide and addition of a gap between
    the source / guide. It does not contain code for providing a McStas source
    component in the add_to_instrument method, which the derived class needs
    to overwrite.

    The Parameter class used allow parameters in the set to be scanned by the
    user, so when a list is given in any number of the parameters, a N
    dimensional space is created that will be mapped. When using these
    parameters in the class, they can be accessed with self[key], and will
    have the appropriate value prepared before the methods of this class are
    called. It is highly advised that additional parameters are given in this
    same manner, as they can then be included in a scan without further work.

    Distance from Source to guide can be handled in a number of ways. The user
    can specify either a fixed distance or a range to the Source, and since
    these are parameters these can be scanned. Any choice made on the
    individual guides are set to overwrite these preferences, as it is then
    possible to test a range of different guides with different starting
    conditions.

    The Source is responsible for adding the space between source and the
    first guide element, which is usually a gap, but could be more advanced.
    A bispectral source could for example include a bispectral switch, and
    it is allowed to add free parameters which would optimize aspects of
    these added components.
    """

    def __init__(self, width, height, guide_start=None, min_guide_start=None, max_guide_start=None, name=None):
        """
        Base class for source used in optimization/characterization of guides

        Sources used in guide_bot should inherit from this class to ensure the
        basic functionality of a source is covered. It is assumed to be a
        rectangular area. The required wavelength area is determined by the
        sample rather than the source, as it is only necessary to simulate
        rays with a wavelength inside that figure of merit. Parameters can be
        scanned to investigate a range of different source / sample
        combinations by providing lists as any of the inputs. Furthermore
        these can be accessed by instance["par_name"], and can be locked
        together with the lock_parameters method.

        Parameters
        ----------

        width : float / list for scan
            Width of the rectangular source in [m]

        height : float / list for scan
            Height of the rectangular source in [m]

        guide_start : float / list for scan
            Given distance from source to start of guide (guides can overwrite)

        min_guide_start : float / list for scan
            Minimum distance from source to guide (guides can overwrite)

        max_guide_start : float / list for scan
            Maximum distance from source to guide (guides can overwrite)
            
        name : str
            Name of the source instance
        """
        if name is None:
            name = type(self).__name__
        self.set_name(name)
        
        self.parameters = Parameters()

        self.parameters.add("width", width, unit="m")
        self.parameters.add("height", height, unit="m")

        self.parameters.add("guide_start", guide_start, unit="m")
        self.parameters.add("min_guide_start", min_guide_start, unit="m")
        self.parameters.add("max_guide_start", max_guide_start, unit="m")

    def __getitem__(self, item):
        """
        Ensures an instance can access the underlying parameters with ["par"]

        When scanning the different requested moderators, the Parameter
        container is updated internally so it returns the current values of
        the parameters instead of the list initially given. This method
        allows the use of the [] operator to access the parameter element
        values.

        Parameters
        ----------

        item : str
            Name of parameter for which the value is requested
        """
        return self.parameters[item]
    
    def set_name(self, name):
        """
        Set the name of the source instance
        
        Raises NameError if an illegal character is found in the given
        
        Parameters
        ----------

        name : str
            New name of source
    
        """
        illegal_characters = [" ", "/", "\\"]
        for illegal_character in illegal_characters:
            if illegal_character in name:
                raise RunTimeError("Illegal character in name '" + illegal_character + "' found.")

        if not type(name) == str:
            raise RunTimeError("Name given not a string")

        self.name = name

    def make_name_unique(self, name_list):
        """
        Makes name of the source unique when some names are already given

        Parameters
        ----------
        current_name_list : list
            List of currently used names
        """

        base_name = self.get_name()
        index = 0
        while(self.get_name() in name_list):
            self.set_name(base_name + "_" + str(index))
            index += 1

    def get_name(self):
        """
        Get the name of

        Returns
        -------
        name : str
            Name of source instance
        """
        return self.name

    def lock_parameters(self, par1, par2):
        """
        Lock the scan of two parameters together

        All scanned parameters are assumed independent so a map of all
        combinations is investigated. By locking two parameters together,
        these are considered a single parameter scanned and thus this requires
        they have the same number of scan steps, i.e. length of lists.

        Parameters
        ----------

        par1 : str
            Name of first parameter to lock

        par2 : str
            Name of second parameter to lock
        """
        self.parameters.lock_parameters(par1, par2)

    def add_to_instrument(self, instrument, instrument_parameters, first_element):
        """
        Add to instrument adds McStas code describing the source

        The BaseSource does not contain any instrument code, but defines this
        method to ensure it is overwritten by the object that inherits from
        the BaseSource. It is intended that a McStas source is added that
        uses the input parameters for width / height etc. The wavelength range
        is given in the lambda_range input, which is a list with min/max. The
        first element is also available, this can be used to for example set
        the focus of the source to the opening of that. Finally it is possible
        to add parameters which should be optimized to the
        instrument_parameters, this could for example be position/angle of the
        guide relative to the source.

        Parameters
        ----------

        instrument : McStasScript instr object
            Instrument object which the source should be added to

        instrument_parameters : InstrumentParameterContainer object
            Parameter container where parameters can be added for optimization

        lambda_range : list of floats or str (parameter names)
            Minimum and maximum wavelength that needs to be simulated

        first_element : GuideElement
            The first user provided GuideElement after the source
        """
        raise RuntimeError("Using BaseSource directly, or derived didn't override add_to_instrument.")

    def create_brilliance_reference_instrument(self, scan_name, instrument_parameters, sample):
        """
        Creates instrument object meant for obtaining brilliance reference

        In order to calculate the brilliance transfer, a reference close to
        the source is needed. This method sets up a instrument with only the
        source described by this object, and a sample. Brilliance transfer
        is the ratio of phase-space density, and so it is usually calculated
        by dividing the intensity from two identical monitors, one at the
        source and one at the investigated position. They both need to be
        closed phase-space volumes in the sense that they must have limits in
        wavelength, divergence and space. The limits can however be different
        if this is taken into account in the normalization, and that the
        density is assumed constant. In some instances it is needed to
        calculate brilliance transfer to a monitor larger than the moderator,
        and so the investigated monitor is decreased to a small size here
        and the smaller size is taken into account during the normalization.
        The brilliane monitors provided by the given sample object are placed
        at such a distance so they are fully illuminated by the source, this
        distance is calculated for horizontal and vertical direction where
        the minimum is selected. This methods does not need to be overwritten
        by user provided source objects, unless the positioning of the
        figure of merit monitors need to be changed.

        Parameters
        ----------

        scan_name : str
            Base of instrument name

        instrument_parameters : InstrumentParameterContainer
            Contains instrument_parameters for the source, usually empty

        sample : guide_bot sample object
            Sample object describing the figure of merit
        """

        # define small monitor size
        small_xwidth = 0.001
        small_yheight = 0.001

        # reduce size of all monitors
        # Start the instrument object
        instrument = instr.McStas_instr(scan_name + "_brill_ref")
        instrument.add_component("Origin", "Progress_bar")

        instrument_parameters.set_current_category("brilliance")
        min_div_horizontal, min_div_vertical = sample.add_brilliance_analysis_to_instrument(instrument, instrument_parameters)

        # Reduce size of all monitors
        components = instrument.component_list
        for component in components:
            if hasattr(component, "xwidth"):
                component.xwidth = small_xwidth
                component.yheight = small_yheight # will fail if no yheight, want that error

        # make dummy Element correct start point and dimensions
        dummy = GuideElement(name="moderator_guide_gap", start_point=0,
                             start_width=self["width"], start_height=self["height"],
                             end_width=small_xwidth, end_height=small_yheight)

        dummy.setup_instrument_and_parameters(instrument, instrument_parameters)
        instrument_parameters.add_parameter(dummy.end_width)
        instrument_parameters.add_parameter(dummy.end_height)
        instrument_parameters.add_parameter(dummy.start_point)

        sample.add_sample_info(instrument_parameters)

        # Calculate the suitable distance in this case
        # need largest divergence in each direction
        source_width = self["width"]
        distance_horizontal = 0.5*(source_width - small_xwidth)/math.tan(min_div_horizontal*np.pi/180)

        source_height = self["height"]
        distance_vertical = 0.5*(source_height-small_yheight)/math.tan(min_div_vertical*np.pi/180)

        monitor_distance = min(distance_horizontal, distance_vertical)

        # overwrite its get_length method for convenience
        dummy.get_length_name = lambda : monitor_distance

        # Add arm to distance moderator and the sample monitors
        arm = instrument.add_component("FOM_position", "Arm", after="Origin")
        arm.set_AT([0, 0, monitor_distance], RELATIVE="PREVIOUS")

        # Add source to the instrument
        instrument_parameters.set_current_category("moderator")
        self.add_to_instrument(instrument, instrument_parameters, dummy)

        instrument_parameters.export_to_instrument(instrument)

        return instrument

    def apply_guide_start(self, guide):
        """
        Logic for adjusting the starting distance of guide based on preferences

        The source needs to have some base values for distance between source
        and the guide, but these can be overwritten by the individually
        provided guides in order to allow testing a range of starting
        conditions. In cases where a range was specified by the source, but
        only one of the limits are provided by the guide, only that one is
        overwritten.

        Parameters
        ----------

        guide : Guide object
            User given Guide before add_start method of Source is performed
        """
        if self["guide_start"] is None and (self["min_guide_start"] is None or self["max_guide_start"] is None):
            raise ValueError("Source need either guide_start or min_guide_start and max_guide_start specified.")

        if self["guide_start"] is not None:
            fixed_start_from_source = True
            if self["min_guide_start"] is not None or self["max_guide_start"] is not None:
                raise ValueError("When guide_start is set, min_guide_start and max_guide_start can not be set.")
        else:
            fixed_start_from_source = False
            if self["min_guide_start"] is None or self["max_guide_start"] is None:
                raise ValueError("Need to set both min_guide_start and max_guide_start.")

        # Grab the first element of the guide to see what the user specified in terms of start distance
        first_element = guide.guide_elements[0]
        first_element_sp = first_element.start_point
        if isinstance(first_element_sp, ipars.RelativeFreeInstrumentParameter):
            given_min_start = first_element_sp.get_lower_static_bound()
            given_max_start = first_element_sp.get_upper_static_bound()
            if given_min_start is None and given_max_start is None:
                # This is the default value, so the user did not specify start_point
                if fixed_start_from_source:
                    first_element.start_point = ipars.FixedInstrumentParameter("guide_start", self["guide_start"])
                else:
                    first_element.start_point = ipars.FreeInstrumentParameter("guide_start", self["min_guide_start"],
                                                                              self["max_guide_start"])
            else:
                # The user specified something, check if any information is lacking
                if given_min_start is None:
                    # A minimum is missing, use minimum from source
                    first_element_sp.static_lower = self["min_guide_start"]
                if given_max_start is None:
                    # A maximum is missing, use maximum from source
                    first_element_sp.static_upper = self["max_guide_start"]

    def add_start(self, guide, instrument_parameters):
        """
        Adds GuideElement to Guide describing what is between source and guide

        In most cases there is just a Gap between the source and the guide,
        which is what will be insterted from the BaseSource. One could imagine
        sources with some other element, perhaps reflector parts, that can be
        added. These can be optimized or have fixed values as if they were
        provided by the user.

        Parameters
        ----------

        guide : Guide object
            Guide object after apply_guide_start method has been performed

        instrument_parameters : InstrumentParameterContainer
            Parameter container where parameters can be added for optimization
        """

        start_gap = Element_gap.Gap(name="moderator_guide_gap", start_width=self["width"], start_height=self["height"])
        guide.add_guide_element_at_start(start_gap)


class Moderator(BaseSource):
    """
    Simple example of a guide_bot source inheriting from BaseSource

    Simple rectangular source description with constant intensity as a
    function of wavelength. Uses the McStas component Source_simple.
    """

    def __init__(self, *args, **kwargs):
        """
        Simple example of a guide_bot source inheriting from BaseSource

        Simple rectangular source description with constant intensity as a
        function of wavelength. Uses the McStas component Source_simple.

        Parameters
        ----------

        width : float / list for scan
            Width of the rectangular source in [m]

        height : float / list for scan
            Height of the rectangular source in [m]

        guide_start : float / list for scan
            Given distance from source to start of guide (guides can overwrite)

        min_guide_start : float / list for scan
            Minimum distance from source to guide (guides can overwrite)

        max_guide_start : float / list for scan
            Maximum distance from source to guide (guides can overwrite)
        """
        super().__init__(*args, **kwargs)

    def add_to_instrument(self, instrument, instrument_parameters, first_element):
        """
        Add to instrument adds McStas code describing the source

        Here adding the Source_simple component after origin with the
        parameters contained in the object and given in the method input.

        Parameters
        ----------

        instrument : McStasScript instr object
            Instrument object which the source should be added to

        instrument_parameters : InstrumentParameterContainer object
            Parameter container where parameters can be added for optimization

        first_element : GuideElement
            The first user provided GuideElement after the source
        """

        src = instrument.add_component("Moderator", "Source_simple", after="Origin")

        src.xwidth = self["width"]
        src.yheight = self["height"]

        src.dist = first_element.get_length_name()
        src.focus_xw = first_element.end_width.name
        src.focus_yh = first_element.end_height.name

        # min / max_wavelength parameters always defiend by sample
        src.lambda0 = "0.5 * (min_wavelength + max_wavelength)"
        src.dlambda = "0.5*(max_wavelength - min_wavelength)"

class ModeratorDoubleGap(Moderator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_start(self, guide, instrument_parameters):
        """
        Adds GuideElement to Guide describing what is between source and guide

        In most cases there is just a Gap between the source and the guide,
        which is what will be insterted from the BaseSource. One could imagine
        sources with some other element, perhaps reflector parts, that can be
        added. These can be optimized or have fixed values as if they were
        provided by the user.

        Parameters
        ----------

        guide : Guide object
            Guide object after apply_guide_start method has been performed

        instrument_parameters : InstrumentParameterContainer
            Parameter container where parameters can be added for optimization
        """

        start_gap = Element_gap.Gap(name="moderator_guide_gap_1", start_width=self["width"],
                                    start_height=self["height"])
        guide.add_guide_element_at_start(start_gap)

        start_gap_2 = Element_gap.Gap(name="moderator_guide_gap_2", start_width=1.5*self["width"],
                                    start_height=1.5*self["height"])
        guide.add_guide_element_at_start(start_gap_2)


class ModeratorFree(Moderator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_to_instrument(self, instrument, instrument_parameters, first_element):
        """
        Add to instrument adds McStas code describing the source

        Here adding the Source_simple component after origin with the
        parameters contained in the object and given in the method input.

        Parameters
        ----------

        instrument : McStasScript instr object
            Instrument object which the source should be added to

        instrument_parameters : InstrumentParameterContainer object
            Parameter container where parameters can be added for optimization

        first_element : GuideElement
            The first user provided GuideElement after the source
        """

        src = instrument.add_component("Moderator", "Source_simple", after="Origin")

        mod_pos = ipars.FreeInstrumentParameter("mod_position", -0.1, 0.1)
        instrument_parameters.add_parameter(mod_pos)

        src.set_AT([0, "mod_position", 0], RELATIVE="Origin")

        src.xwidth = self["width"]
        src.yheight = self["height"]

        src.dist = first_element.get_length_name()
        src.focus_xw = first_element.end_width.name
        src.focus_yh = first_element.end_height.name

        # min / max_wavelength parameters always defiend by sample
        src.lambda0 = "0.5 * (min_wavelength + max_wavelength)"
        src.dlambda = "0.5*(max_wavelength - min_wavelength)"