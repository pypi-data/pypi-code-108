import math

import numpy as np
import yaml

from guide_bot.requirements.requirement_parameters import Parameters
from guide_bot.parameters import instrument_parameters as ipars
from guide_bot.elements import Element_gap

from mcstasscript.interface import instr, plotter, functions


class Sample:
    """
    Sample class that sets figure of merit for the optimized guide

    The Sample class describes the figure of merit for the guide, including
    the beam size, divergence, wavelength range and distance from source to
    sample. Distance between guide and sample is also set. The parameters
    describing these aspects can all be scanned to perform optimization for
    each combination the user wish to investigate.

    The figure of merit needs to be measured in the McStas simulation, so part
    of the responsibilities of the class is to add a monitor component to the
    McStas instrument file.

    The Sample class is also responsible for adding elements between the guide
    given by the user and the target, which is must often just a gap. This
    could however be something different, and may need optimization, so this
    responsibility has been placed in the Sample class.

    It is straight forward to inherit from this Sample object and adjust the
    figure of merit accordingly. Samples that inherit from this should call
    super().__init__(*args, **kwargs) early in order to set up Parameters.

    The Parameters in the sample can be accessed with Sample["par_name"],
    and will return the current value in case of a scan, not the entire list
    for the scan.
    """
    def __init__(self, width, height,
                 div_horizontal, div_vertical,
                 min_wavelength, max_wavelength,
                 instrument_length, sample_guide_distance,
                 calculate_guide_end_dimensions=True):
        """
        Description of figure of merit for guide optimization

        All given parameters can be scanned by providing an list of floats
        instead of just a single float. All Parameters can be read using
        Sample["par_name"], and will return the current value instead of the
        entire list for the scan.

        Parameters
        ----------

        width : float or list of floats for scan
            Width of beam at sample position in [m]

        height : float or list of floats for scan
            Height of beam at sample position in [m]

        div_horizontal : float or list of floats for scan
            Horizontal beam divergence figure of merit in [deg]

        div_vertical : float or list of floats for scan
            Vertical beam divergence figure of merit in [deg]

        min_wavelength : float or list of floats for scan
            Minimum wavelength in figure of merit [Å]

        max_wavelength : float or list of floats for scan
            Maximum wavelength in figure of merit [Å]

        instrument_length : float or list of floats for scan
            Distance from source to sample in [m]

        sample_guide_distance : float or list of floats for scan
            Distance from guide end to sample in [m]

        calculate_guide_end_dimensions: bool or list of bools for scan (default True)
            If true, the guides end dimensions are calculated from sample requirements
        """
        self.parameters = Parameters()

        # Required
        self.parameters.add("width", width, unit="m")
        self.parameters.add("height", height, unit="m")
        self.parameters.add("div_horizontal", div_horizontal, unit="deg")
        self.parameters.add("div_vertical", div_vertical, unit="deg")
        self.parameters.add("min_wavelength", min_wavelength, unit="AA")
        self.parameters.add("max_wavelength", max_wavelength, unit="AA")
        self.parameters.add("instrument_length", instrument_length, unit="m")
        self.parameters.add("sample_guide_distance", sample_guide_distance, unit="m")

        # Optional (has default value)
        self.parameters.add("calculate_guide_end_dimensions", calculate_guide_end_dimensions, unit="bool")

        # list of PlotInfo objects that will be applied to control plotting with McStasScript
        self.plot_info = PlotInfoContainer()

        # Sample dimensions set during setup for each guide and retrieved from parameters object
        self.sample_width = None
        self.sample_height = None
        self.sample_gap = None

    def __getitem__(self, item):
        """
        Ensures Sample["par_name"] returns value in parameters

        Parameter
        ---------

        item : str
            Name of the parameter to be retrieved
        """
        return self.parameters[item]

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

    def add_sample_info(self, instrument_parameters):
        """
        Adds wavelength parameters to instrument_parameters

        Parameters
        ----------

        instrument_parameters : InstrumentParameterContainer
            Parameter container where parameters can be added for optimization
        """

        min_wavelength = ipars.FixedInstrumentParameter("min_wavelength", self["min_wavelength"])
        max_wavelength = ipars.FixedInstrumentParameter("max_wavelength", self["max_wavelength"])

        instrument_parameters.add_parameter(min_wavelength)
        instrument_parameters.add_parameter(max_wavelength)

        self.sample_width = ipars.FixedInstrumentParameter("sample_width", self["width"])
        self.sample_height = ipars.FixedInstrumentParameter("sample_height", self["width"])

        instrument_parameters.add_parameter(self.sample_width)
        instrument_parameters.add_parameter(self.sample_height)

    def get_size_parameters(self):
        """
        Returns sample size as parameters, only call after add_sample_info

        This relies on the sample being set up already, otherwise it would
        return information from the previous scan point.
        """

        return [self.sample_width, self.sample_height]

    def add_to_instrument(self, instrument, instrument_parameters):
        """
        Adds a figure of merit monitor to the McStas instrument file

        Adds a monitor that will measure the figure of merit. The method
        returns the wavelength range.

        Parameters
        ----------

        instrument : McStasScript instrument object
            Instrument object to which the monitor is added

        instrument_parameters : InstrumentParameterContainer
            Parameter container where parameters can be added for optimization
        """

        mon = instrument.add_component("mon", "Divergence_monitor")

        mon.nh = 20
        mon.nv = 20
        mon.filename = '"fom.dat"'
        mon.maxdiv_h = self["div_horizontal"]
        mon.maxdiv_v = self["div_vertical"]
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 0], RELATIVE=self.sample_gap.end_component_name)

        return [self["min_wavelength"], self["max_wavelength"]]

    def add_end(self, guide, instrument_parameters):
        """
        Adds GuideElements between user provided guide and the sample

        Most often a Gap is added between the provided guide and the sample,
        but this method provides the flexibility to do something different.

        Parameters
        ----------

        guide : Guide object
            Guide object after apply_guide_start method has been performed

        instrument_parameters : InstrumentParameterContainer
            Parameter container where parameters can be added for optimization
        """

        # Use minimalist principle to calculate guide end dimensions
        width = self["width"] + 2 * math.tan(self["div_horizontal"] * math.pi / 180.0) * self["sample_guide_distance"]
        height = self["height"] + 2 * math.tan(self["div_vertical"] * math.pi / 180.0) * self["sample_guide_distance"]

        if self["calculate_guide_end_dimensions"]:
            # If end dimensions should be calculated, use exact values
            width_input = width
            height_input = height
        else:
            # If end dimensions should be optimized, use calculated values to set reasonable limits
            width_input = [0.5*width, 1.5*width]
            height_input = [0.5*height, 1.5*height]

        self.sample_gap = Element_gap.Gap(name="guide_sample_gap",
                                       length=self["sample_guide_distance"],
                                       start_width=width_input, start_height=height_input)

        guide.add_guide_element(self.sample_gap)

    def add_analysis_to_instrument(self, instrument, instrument_parameters):
        """
        Adds monitors for beam analysis to instrument file

        After successful optimization the beam from the guide is analyzed with
        more monitors than during the optimization. These can save more data,
        and the simulations can be performed with a much greater ncount for
        better quality.

        Parameters
        ----------

        instrument : McStasScript instrument object
            Instrument object to which the monitor is added
        """

        mon = instrument.add_component("psd_lin_horizontal", "PSDlin_monitor")
        mon.nx = 300
        mon.filename = '"psd_lin_horizontal.dat"'
        mon.xwidth = "2.0*sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 0], RELATIVE=self.sample_gap.end_component_name)

        info = self.plot_info.new(mon, title="Horizontal position")
        info.set_xlabel("Horizontal position [cm]")
        info.set_plot_options(x_axis_multiplier=100)

        mon = instrument.add_component("psd_lin_vertical", "PSDlin_monitor")
        mon.nx = 300
        mon.filename = '"psd_lin_vertical.dat"'
        mon.xwidth = "2.0*sample_height"
        mon.yheight = "sample_width"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 90], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new("psd_lin_vertical", title="Vertical position")
        info.set_xlabel("Vertical position [cm]")
        info.set_plot_options(x_axis_multiplier=100)

        mon = instrument.add_component("divergence_horizontal", "Hdiv_monitor")
        mon.nh = 200
        mon.filename = '"divergence_horizontal.dat"'
        mon.h_maxdiv = 2*self["div_horizontal"]
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Horizontal divergence")
        info.set_xlabel("Horizontal divergence [deg]")

        mon = instrument.add_component("divergence_vertical", "Hdiv_monitor")
        mon.nh = 200
        mon.filename = '"divergence_vertical.dat"'
        mon.h_maxdiv = 2*self["div_vertical"]
        mon.xwidth = "sample_height"
        mon.yheight = "sample_width"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 90], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Vertical divergence")
        info.set_xlabel("Vertical divergence [deg]")

        mon = instrument.add_component("psd_analysis_large", "PSD_monitor")
        mon.nx = 300
        mon.ny = 300
        mon.filename = '"psd_large.dat"'
        mon.xwidth = "2.0*sample_width"
        mon.yheight = "2.0*sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Large PSD")
        info.set_xlabel("Horizontal position [cm]")
        info.set_ylabel("Vertical position [cm]")

        mon = instrument.add_component("divergence_2D", "Divergence_monitor")
        mon.nh = 200
        mon.nv = 200
        mon.filename = '"divergence_2D.dat"'
        mon.maxdiv_h = 2*self["div_horizontal"]
        mon.maxdiv_v = 2*self["div_vertical"]
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Divergence 2D")
        info.set_xlabel("Horizontal divergence [deg]")
        info.set_ylabel("Vertical divergence [deg]")

        mon = instrument.add_component("Lambda", "L_monitor")
        mon.Lmin = "min_wavelength"
        mon.Lmax = "max_wavelength"
        mon.nL = 200
        mon.filename = '"wavelength.dat"'
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Wavelength")
        info.set_xlabel("Wavelength [AA]")

        mon = instrument.add_component("Acceptance_horizontal", "DivPos_monitor")
        mon.nh = 200
        mon.ndiv = 200
        mon.filename = '"Acceptance_horizontal.dat"'
        mon.maxdiv_h = 2*self["div_horizontal"]
        mon.xwidth = "2.0*sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Acceptance horizontal")
        info.set_xlabel("Horizontal position [cm]")
        info.set_ylabel("Horizontal divergence [deg]")
        info.set_plot_options(x_axis_multiplier=100)

        mon = instrument.add_component("Acceptance_vertical", "DivPos_monitor")
        mon.nh = 200
        mon.ndiv = 200
        mon.filename = '"Acceptance_vertical.dat"'
        mon.maxdiv_h = 2 * self["div_vertical"]
        mon.xwidth = "2.0*sample_height"
        mon.yheight = "sample_width"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 90], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Acceptance vertical")
        info.set_xlabel("Vertical position [cm]")
        info.set_ylabel("Vertical divergence [deg]")
        info.set_plot_options(x_axis_multiplier=100)

        mon = instrument.add_component("psd_analysis", "PSD_monitor")
        mon.nx = 300
        mon.ny = 300
        mon.filename = '"psd.dat"'
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="PSD sample size")
        info.set_xlabel("Horizontal position [cm]")
        info.set_ylabel("Vertical position [cm]")

        mon = instrument.add_component("divergence_2D_fom", "Divergence_monitor")
        mon.nh = 200
        mon.nv = 200
        mon.filename = '"divergence_2D_fom.dat"'
        mon.maxdiv_h = self["div_horizontal"]
        mon.maxdiv_v = self["div_vertical"]
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal")

        info = self.plot_info.new(mon, title="Divergence 2D sample size")
        info.set_xlabel("Horizontal divergence [deg]")
        info.set_ylabel("Vertical divergence [deg]")

    def add_brilliance_analysis_to_instrument(self, instrument, instrument_parameters):
        """
        Adds monitors for beam analysis in terms of brilliance transfer to instrument

        After successful optimization the beam from the guide is analyzed with
        more monitors than during the optimization. These can save more data,
        and the simulations can be performed with a much greater ncount for
        better quality. The monitors in this part should all have limits for
        divergence and space so that they can be normalized as brilliance
        transfer. The normalization is done by inserting these monitors after
        the same moderator in another instrument, and their signal is used
        to normalize each monitor before plotting.

        Parameters
        ----------

        instrument : McStasScript instrument object
            Instrument object to which the monitor is added

        Returns
        -------
        horizontal and vertical maximum divergence needed : float, float

        """

        instrument.add_declare_var("double", "div_h", comment="Horizontal divergence at sample position")
        instrument.add_declare_var("double", "div_h_limit", value=self["div_horizontal"])
        instrument.add_declare_var("int", "inside_h_div",
                                   comment="Flag specifying if ray is within horizontal div limits or not")

        instrument.add_declare_var("double", "div_v", comment="Vertical divergence at sample position")
        instrument.add_declare_var("double", "div_v_limit", value=self["div_vertical"])
        instrument.add_declare_var("int", "inside_v_div",
                                   comment="Flag specifying if ray is within vertical div limits or not")

        instrument.add_declare_var("int", "inside_div",
                                   comment="Flag specifying if ray is within div limits or not")

        arm = instrument.add_component("fom_check", "Arm", RELATIVE="PREVIOUS")
        arm.append_EXTEND("div_h = RAD2DEG*atan(vx/vz);")
        arm.append_EXTEND("div_v = RAD2DEG*atan(vy/vz);")
        arm.append_EXTEND("if (div_h < div_h_limit && div_h > -div_h_limit) inside_h_div = 1;")
        arm.append_EXTEND("else inside_h_div=0;")
        arm.append_EXTEND("if ( div_v < div_v_limit && div_v > -div_v_limit) inside_v_div = 1;")
        arm.append_EXTEND("else inside_v_div=0;")
        arm.append_EXTEND("if (inside_h_div == 1 && inside_v_div == 1) inside_div = 1;")
        arm.append_EXTEND("else inside_div=0;")

        mon = instrument.add_component("psd_lin_horizontal_brill", "PSDlin_monitor")
        mon.nx = 300
        mon.filename = '"psd_lin_horizontal_brill.dat"'
        mon.xwidth = "2.0*sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_WHEN("inside_div == 1")

        info = self.plot_info.new(mon, title="Linear PSD")
        info.set_xlabel("Horizontal position [cm]")
        info.set_ylabel("Brilliance transfer [1]")
        info.set_plot_options(x_axis_multiplier=100)

        mon = instrument.add_component("psd_lin_vertical_brill", "PSDlin_monitor")
        mon.nx = 300
        mon.filename = '"psd_lin_vertical_brill.dat"'
        mon.xwidth = "2.0*sample_height"
        mon.yheight = "sample_width"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 90], RELATIVE="psd_lin_horizontal_brill")
        mon.set_WHEN("inside_div == 1")

        info = self.plot_info.new(mon, title="Linear PSD")
        info.set_xlabel("Vertical position [cm]")
        info.set_ylabel("Brilliance transfer [1]")
        info.set_plot_options(x_axis_multiplier=100)

        mon = instrument.add_component("divergence_horizontal_brill", "Hdiv_monitor")
        mon.nh = 200
        mon.filename = '"divergence_horizontal_brill.dat"'
        mon.h_maxdiv = 2 * self["div_horizontal"]
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal_brill")
        mon.set_WHEN("inside_v_div == 1")

        info = self.plot_info.new(mon, title="Linear divergence")
        info.set_xlabel("Horizontal divergence [deg]")
        info.set_ylabel("Brilliance transfer [1]")

        mon = instrument.add_component("divergence_vertical_brill", "Hdiv_monitor")
        mon.nh = 200
        mon.filename = '"divergence_vertical_brill.dat"'
        mon.h_maxdiv = 2 * self["div_vertical"]
        mon.xwidth = "sample_height"
        mon.yheight = "sample_width"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 90], RELATIVE="psd_lin_horizontal_brill")
        mon.set_WHEN("inside_h_div == 1")

        info = self.plot_info.new(mon, title="Linear divergence")
        info.set_xlabel("Vertical divergence [deg]")
        info.set_ylabel("Brilliance transfer [1]")

        mon = instrument.add_component("Lambda_brill", "L_monitor")
        mon.Lmin = "min_wavelength"
        mon.Lmax = "max_wavelength"
        mon.nL = 200
        mon.filename = '"wavelength_brill.dat"'
        mon.xwidth = "sample_width"
        mon.yheight = "sample_height"
        mon.restore_neutron = 1
        mon.set_AT([0, 0, 1E-6], RELATIVE="PREVIOUS")
        mon.set_ROTATED([0, 0, 0], RELATIVE="psd_lin_horizontal_brill")
        mon.set_WHEN("inside_div == 1")

        info = self.plot_info.new(mon, title="Wavelength")
        info.set_xlabel("Wavelength [AA]")
        info.set_ylabel("Brilliance transfer [1]")

        return 2*self["div_horizontal"], 2*self["div_vertical"]

    def perform_analysis(self, instrument, instrument_brill_ref, parameters, settings):
        """
        Performs analysis of the optimized guide using McStasScript

        After the guide has been optimized, it is characterized by performing
        simulations using the optimal parameters and the additional monitors
        added by the add_analysis_to_instrument method of this class. Here
        a number of wavelength snapshots are defined, and simulations are
        performed with these wavelength ranges. A simulation with a wavelength
        interval larger than the figure of merit is also added. All results
        are plotted and saved to disk in the folder describing the current
        run. This method is intended to be overwritten by the user in order to
        customize how the optimized guides are characterized and the final
        results are presented.

        Parameters
        ---------

        instrument : McStasScript instrument object
            Instrument with current moderator and added analysis monitors

        instrument_brill_ref : McStasScript instrument object
            Instrument with only current moderator and brilliance monitors

        parameters : Dict
            Found optimal parameters for the guide system

        settings : Dict
            Settings for running simulation, optional to use these
        """

        snapshot_centers = np.linspace(self["min_wavelength"], self["max_wavelength"], 3)
        snapshot_widths = 0.01

        snapshot_minimums = snapshot_centers - 0.5 * snapshot_widths
        snapshot_maximums = snapshot_centers + 0.5 * snapshot_widths

        for min_wavelength, max_wavelength, center in zip(snapshot_minimums, snapshot_maximums, snapshot_centers):
            name = "Snapshot_" + str(center) + "_AA"

            parameters["min_wavelength"] = min_wavelength
            parameters["max_wavelength"] = max_wavelength

            sim_data = run_simulation(name, parameters, settings, instrument)
            ref_data = run_simulation_brill(name + "_brill", parameters, settings, instrument_brill_ref) # will have too many parameters and unrecoignized

            normalize_brill_ref(sim_data, ref_data, instrument, instrument_brill_ref)

            self.plot_info.apply_all_data(sim_data)
            #self.plot_info.apply_all_data(ref_data) # Doesnt handle case where not all found

            plotter.make_sub_plot(sim_data[0:6], filename=name + "_1.png")
            plotter.make_sub_plot(sim_data[6:11], filename=name + "_2.png")
            plotter.make_sub_plot(sim_data[11:], filename=name + "_3.png")
            plotter.make_sub_plot(ref_data, filename=name + "_ref.png")

        name = "large_wavelength_band"
        parameters["min_wavelength"] = 0.5 * self["min_wavelength"]
        parameters["max_wavelength"] = 2.0 * self["max_wavelength"]

        sim_data = run_simulation(name, parameters, settings, instrument)
        ref_data = run_simulation_brill(name + "_brill", parameters, settings, instrument_brill_ref)  # will have too many parameters and unrecoignized

        normalize_brill_ref(sim_data, ref_data, instrument, instrument_brill_ref)

        self.plot_info.apply_all_data(sim_data)
        #self.plot_info.apply_all_data(ref_data) # Doesnt handle case where not all found

        plotter.make_sub_plot(sim_data[0:6], filename=name + "_1.png")
        plotter.make_sub_plot(sim_data[6:11], filename=name + "_2.png")
        plotter.make_sub_plot(sim_data[11:], filename=name + "_3.png")
        plotter.make_sub_plot(ref_data, filename=name + "_ref.png")

        name = "fom_wavelength_band"
        parameters["min_wavelength"] = self["min_wavelength"]
        parameters["max_wavelength"] = self["max_wavelength"]

        sim_data = run_simulation(name, parameters, settings, instrument)
        ref_data = run_simulation_brill(name + "_brill", parameters, settings,
                                        instrument_brill_ref)  # will have too many parameters and unrecoignized

        normalize_brill_ref(sim_data, ref_data, instrument, instrument_brill_ref)

        self.plot_info.apply_all_data(sim_data)
        # self.plot_info.apply_all_data(ref_data) # Doesnt handle case where not all found

        plotter.make_sub_plot(sim_data[0:6], filename=name + "_1.png")
        plotter.make_sub_plot(sim_data[6:11], filename=name + "_2.png")
        plotter.make_sub_plot(sim_data[11:], filename=name + "_3.png")
        plotter.make_sub_plot(ref_data, filename=name + "_ref.png")


class PlotInfo:
    """
    Contains information on options for plotting a McStasScript dataset

    Container for information for McStasScript monitor options including
    methods for applying these monitors to a specific monitor or in a
    larger dataset.
    """
    def __init__(self, mon_name, title=None, xlabel=None, ylabel=None, plot_options=None):
        """
        Sets up a PlotInfo object with initial settings

        The PlotInfo object describes how a McStasScript object should be
        plotted and can be applied to a monitor or dataset. It is required to
        provide a name for the monitor or a McStasScript component instance
        so the monitor can be found in a dataset.

        Parameters
        ----------

        mon_name : str or McStasScript component object
            Name of monitor to be adjusted

        title : str
            Title of the plot

        xlabel : str
            xlabel of the plot

        ylabel : str
            ylabel of the plot

        plot_options : dict
            Dictionary with any McStasScript plot options to be applied
        """
        if isinstance(mon_name, str):
            self.mon_name = mon_name
        else:
            # In case it is a McStasScript component object
            self.mon_name = mon_name.name

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        if plot_options is None:
            self.plot_options = {}
        else:
            self.plot_options = plot_options

    def set_title(self, title):
        """
        Sets title of the plot

        Parameters
        ----------

        title : str
            String for plot title
        """
        self.title = title

    def set_xlabel(self, xlabel):
        """
        Sets xlabel of the plot

        Parameters
        ----------

        xlabel : str
            String for xlabel
        """
        self.xlabel = xlabel

    def set_ylabel(self, ylabel):
        """
        Sets ylabel of the plot

        Parameters
        ----------

        ylabel : str
            String for ylabel
        """
        self.ylabel = ylabel

    def set_plot_options(self, **kwargs):
        """
        Sets plot_options for the plot

        Parameters
        ----------

        keyword arguments : McStasScript plot_option arguments
            All arguments that can be given to McStasData set_plot_options
        """
        self.plot_options.update(**kwargs)

    def apply_to_single(self, data):
        """
        Applies settings to a data object

        Parameters
        ----------

        data : McStasScript McStasData object
        """
        data.set_title(self.title)
        data.set_xlabel(self.xlabel)
        data.set_ylabel(self.ylabel)
        data.set_plot_options(**self.plot_options)

    def apply_to_data(self, dataset):
        """
        Applies settings to matching object in dataset

        Parameters
        ----------

        dataset : list of McStasScript McStasData objects
            dataset that contains monitor to apply settings to
        """
        mon = functions.name_search(self.mon_name, dataset)
        self.apply_to_single(mon)


class PlotInfoContainer:
    def __init__(self):
        self.infos = []

    def new(self, *args, **kwargs):
        info = PlotInfo(*args, **kwargs)
        self.infos.append(info)
        return info

    def apply_all_data(self, data):
        for info in self.infos:
            info.apply_to_data(data)


def run_simulation(name, parameters, settings, instrument):
    """
    Performs the McStasScript instrument simulation with given settings

    Parameters
    ----------

    name : str
        Name of the folder to be created with the raw data

    parameters : Dict
        Parameters to be used for the simulation

    settings : Dict
        Settings to be used for the simulation

    instrument : McStasScript instrument object
        Instrument which will be used for the simulation
    """
    write_component_dimensions(name, instrument)

    if "ncount_analysis" in settings:
        ncount = settings["ncount_analysis"]
    else:
        ncount = 10*settings["ncount"]

    return instrument.run_full_instrument(foldername=name,
                                          increment_folder_name=True,
                                          parameters=parameters,
                                          ncount=ncount)

def run_simulation_brill(name, parameters, settings, instrument):
    """
    Performs the McStasScript instrument simulation with given settings

    Parameters
    ----------

    name : str
        Name of the folder to be created with the raw data

    parameters : Dict
        Parameters to be used for the simulation

    settings : Dict
        Settings to be used for the simulation

    instrument : McStasScript instrument object
        Instrument which will be used for the simulation
    """

    write_component_dimensions(name, instrument)

    if "ncount_analysis" in settings:
        ncount = settings["ncount_analysis"]
    else:
        ncount = 10*settings["ncount"]

    reduced_parameters = {}
    for parameter in instrument.parameter_list:
        if parameter.name in parameters:
            reduced_parameters[parameter.name] = parameters[parameter.name]

    return instrument.run_full_instrument(foldername=name,
                                          increment_folder_name=True,
                                          parameters=reduced_parameters,
                                          ncount=ncount)


def normalize_brill_ref(data, ref_data, instrument, ref_instrument):
    """
    Performs brilliance transfer normalization for a McStasScript dataset

    When normalizing to brilliance transfer, a intensity data is divided with
    reference data from close to the source. It is required that each data
    set has closed phase-space bounderies in both wavelength, space and
    divergence for this normalization to make sense. The reference data set
    should be evenly illuminated in this space. It is however possible to
    have different phase-space boarders for the data and reference, if this
    is taken into account during the normalization. Here it is assumed the
    divergence and wavelength limits are equal, but the spatial limits can be
    different. The instrument objects for each data set is used to check
    these sizes for use in the normalization.

    Parameters
    ----------

    data : list of McStasData objects
        List of data that will be normalized when twin is found in ref_data

    ref_data : list of McStasData objects
        List of data that will be used for normalization

    instrument : McStasScript instrument object
        Instrument object corresponding to the data

    ref_instrument : McStasScript instrument object
        Instrument object corresponding to the ref_data
    """

    ref_data_names = []
    for data_object in ref_data:
        ref_data_names.append(data_object.name)

    normalized_monitors = []
    for data_object in data:
        if data_object.name in ref_data_names:
            ref_data_object = functions.name_search(data_object.name, ref_data)

            monitor = instrument.get_component(data_object.name)
            ref_monitor = ref_instrument.get_component(data_object.name)

            mon_area = get_monitor_area(data_object, monitor)
            ref_mon_area = get_monitor_area(ref_data_object, ref_monitor)

            if mon_area is None or ref_mon_area is None:
                raise RuntimeError("Area could not be read!")

            area_ratio = mon_area/ref_mon_area

            # normalize pixel for pixel (always allowed, but less efficient)
            data_object.Intensity /= ref_data_object.Intensity*area_ratio
            data_object.Error = np.sqrt(data_object.Error**2 + ref_data_object.Error**2)

            normalized_monitors.append(data_object.name)

            # Could detect situations where it is allowed to sum/average reference
            #  but this depends on whether for example intensity is constant with
            #  wavelength.

    return normalized_monitors


def write_component_dimensions(base_name, instrument):
    component_x_y = {}
    for comp_name in instrument.component_name_list:
        comp = instrument.get_component(comp_name)

        if hasattr(comp, "xwidth") and hasattr(comp, "yheight"):
            component_x_y[comp_name] = [comp.xwidth, comp.yheight]

    with open(base_name + ".yaml", 'w') as yaml_file:
        yaml.dump(component_x_y, yaml_file, default_flow_style=False)


def get_monitor_area(data, component):
    """
    Gets the area of a McStas monitor that use standard xwidth / yheight input

    Parameters
    ----------

    data : McStasData object
        data object that contains parameters used for run

    component : McStasScript component object
        component to check
    """

    width = read_field(data, component, "xwidth")
    height = read_field(data, component, "yheight")

    if width is not None and height is not None:
        return width*height # m^2

    return None


def read_field(data, component, field):
    """
    Reads a field of a component using parameters from given dataset

    data : McStasData object
        data object that contains parameters used for run

    component : McStasScript component object
        component to check

    field : str
        name of component field to check
    """

    # If the component doesnt have the field, return
    if not hasattr(component, field):
        return None

    # Read the input given to that field and parameters of run
    component_field = getattr(component, field)
    used_parameters = data.metadata.parameters

    value = None
    try:
        # If a float or int is given directly, just read that
        value = float(component_field)
    except ValueError:
        # If a parameter name is given directly, look that up
        if component_field in used_parameters:
            value = used_parameters[component_field]

    # Last attempt to read using python eval in case a simple expression is used
    # This will catch for example "2.0*sample_width"
    if value is None:
        try:
            # Try to evaluate field with scope of all instrument parameters
            value = eval(component_field, used_parameters)
        except:
            value = None

    try:
        value = float(value)
    except ValueError:
        # Do not want to return a string
        value = None
    except TypeError:
        value = None

    return value





