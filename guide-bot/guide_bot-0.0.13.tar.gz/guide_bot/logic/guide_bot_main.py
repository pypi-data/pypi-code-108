import copy
import os
import dill
import yaml

from _version import __version__
from guide_bot.parameters import instrument_parameters as ipars
from guide_bot.parameters import instrument_parameter_container as ipars_container
import guide_bot.requirements.requirement_parameters as rpars
from guide_bot.logic import length_system
from guide_bot.elements import Element_gap
from guide_bot.optimizer import optimizer

from mcstasscript.interface import instr, plotter


class Guide:
    """
    Guide with elements and constraints, can be added to McStas instrument

    The main class for describing a neutron guide, internally keeping a list
    of the added guide modules and user defined constraints. In the main logic
    section of guide_bot, the methods of the Guide object are called to
    prepare for optimization. Since elements define their opening dimensions,
    the end dimensions provided by the user are shifted back to the next
    opening dimensions by the transfer_end_specifications method. The Guide
    can add code to a McStasScript instrument object using the
    add_to_instrument method, this is done from sample to source, and the
    previous start dimensions are transferred to the next module in each step.
    """
    def __init__(self, name=None):
        """
        Provides a Guide object that describes a guide with given constraints

        Initially the guide object is empty, and guide elements should be
        added using the add_guide_element method. The collection of guide
        elements can then be added to a McStasScript instrument and optimized
        together. Constraints on user defined parameters can be added directly
        to this Guide object, these will be in addition to the constraints
        defined through the options of the individual modules. Can have a
        current_owner attribute set which sets that owner to Elements added to
        this guide.

        ----------
        Parameters

        name : str
            Optional name of the guide
        """
        self.guide_elements = []

        self.name = name
        self.auto_name = None
        self.generate_name()

        self.original_guide_elements = None

        self.constraints = []

        self.current_owner = None
        self.required_components = set()
    
    def save_original(self):
        """
        Saves the original guide configuration
        """
        self.original_guide_elements = copy.deepcopy(self.guide_elements)

    def restore_original(self):
        """
        Restores to original guide configuration
        """
        self.guide_elements = self.original_guide_elements

    def generate_name(self):
        """
        Generates a name for this guide using first letter of each element
        """

        if self.auto_name is None:
            self.auto_name = self.name is None

        if self.auto_name:
            self.name = "Guide_"
            for element in self.guide_elements:
                first_letter = type(element).__name__[0]
                self.name += first_letter
    
    def make_name_unique(self, all_names):
        """
        Ensures the name of the guide is unique

        Parameters
        ----------

        all_names : list
            List of all guide names used to ensure this name is unique
        """
        suggested_name = self.name
        index = 0
        while suggested_name in all_names:
            suggested_name = self.name + "_Alt" + str(index)
            index += 1

        self.name = suggested_name
        return self.name

    def set_current_owner(self, owner):
        """
        Sets the current owner, added Elements will have this owner specified

        Parameters
        ----------

        owner : str
            Specifies the owner of this Element
        """
        self.current_owner = owner
    
    def add_guide_element(self, guide_element):
        """
        Adds a GuideElement to the Guide object

        This is the main method for adding GuideElements to the guide, this
        is appended to the current list of GuideElements.

        Parameters
        ----------

        guide_element : GuideElement
            New element added to the end of the guide
        """

        # todo: check element name not already in use

        if self.current_owner is not None:
            guide_element.set_owner(self.current_owner)

        self.guide_elements.append(guide_element)
        self.generate_name()

    def __iadd__(self, guide_element):
        """
        Adds a GuideElement to the Guide object with += syntax

        This is the main method for adding GuideElements to the guide, this
        is appended to the current list of GuideElements.

        Parameters
        ----------

        guide_element : GuideElement
            New element added to the end of the guide
        """
        self.add_guide_element(guide_element)

        return self

    def add_guide_element_at_start(self, guide_element):
        """
        Adds a GuideElement to the start of the Guide

        Allows adding a GuideElement to the start of the guide instead of the
        end.

        Parameters
        ----------

        guide_element : GuideElement
            New element added at the start of the guide
        """
        if self.current_owner is not None:
            guide_element.set_owner(self.current_owner)

        # todo: check element name not already in use
        self.guide_elements = [guide_element] + self.guide_elements

    def add_constraint(self, constraint):
        """
        Adds constraint between user defined parameters

        Constraints can be added that uses parameters derived from the
        InstrumentParameter class. These constraints are in addition to those
        defined in the options of the individual guide modules.

        Parameters
        ----------

        constraint : Constraint
            Adds the constraint, will be exported to the optimizer
        """
        self.constraints.append(constraint)

    def export_constraints(self, instrument_parameters):
        """
        Exports the contained constraints to object used by the optimizer

        The modules adds their constraints to instrument_parameters which is
        an instance of InstrumentParameterContainer, and the user defined
        can be exported to this format using this method. In this way the
        optimizer will get both types of constraints in the same system.

        Parameters

        instrument_parameters : InstrumentParameterContainer
            Container to which the Guide constraints are added
        """
        for constraint in self.constraints:
            instrument_parameters.add_constraint(constraint)

    def transfer_end_specifications(self):
        """
        Transfer specified end dimensions to next module as start dimensions

        If end dimensions are specified by the user, they will overwrite the
        start dimensions set at the next module that may or may not have been
        specified by the user.
        """

        for this_guide, next_guide in zip(self.guide_elements[0:-1], self.guide_elements[1:]):
            if this_guide.end_width is not None:
                next_guide.start_width = this_guide.end_width

            if this_guide.end_height is not None:
                next_guide.start_height = this_guide.end_height

    def add_full_instrument(self, instrument, instrument_parameters, moderator, sample):
        """
        Adds McStasScript objects describing this guide to a instrument

        Takes a McStasScript instrument objects and adds the guide modules
        contained in this Guide object to the instrument. This is done from
        the sample to the source, and the start dimensions from each module
        is carried to the next to ensure the guide is closed. The sample and
        moderator is added as well. The wavelength range is contained in the
        sample description, but needed by the moderator, this transfer is
        also performed in this method.

        Parameters
        ----------

        instrument : McStasScript instr object
            Instrument object to which the guide should be added

        instrument_parameters : InstrumentParameterContainer
            The InstrumentParameterContainer with parameters and constraints

        moderator : Object derived from BaseSource
            Description of the source, will be added to the instrument

        sample : Object derived from Sample
            Descrption of sample / figure of merit, will be added to instrument
        """
        sample.add_to_instrument(instrument, instrument_parameters)
        sample.add_wavelength_parameters(instrument_parameters)
        
        sample_width = ipars.FixedInstrumentParameter("sample_width", sample["width"])
        sample_height = ipars.FixedInstrumentParameter("sample_height", sample["height"])
        
        previous_start_dimensions = [sample_width, sample_height]
        
        for guide in reversed(self.guide_elements):
            guide.setup_instrument_and_parameters(instrument, instrument_parameters)
            guide.set_end_dimensions(previous_start_dimensions[0], previous_start_dimensions[1])
            guide.add_to_instr()
            
            previous_start_dimensions = [guide.start_width, guide.start_height]
        
        # Moderator gets the first guide module to set up focusing
        moderator.add_to_instrument(instrument, instrument_parameters, guide)

    def set_instrument_and_instr_parameters(self, instrument, instrument_parameters):
        """
        Sets McStasScript instrument and instrument parameter container

        All elements are informed of the current instrument object and
        instrument parameter container.

        instrument : McStasScript instr object
            Instrument object to which the guide should be added

        instrument_parameters : InstrumentParameterContainer
            The InstrumentParameterContainer with parameters and constraints
        """

        for element in self.guide_elements:
            element.setup_instrument_and_parameters(instrument, instrument_parameters)

    def add_to_instrument(self, sample_dimensions):
        """
        Adds McStasScript objects describing this guide to a instrument

        Takes a McStasScript instrument objects and adds the guide modules
        contained in this Guide object to the instrument. This is done from
        the sample to the source, and the start dimensions from each module
        is carried to the next to ensure the guide is closed. The sample and
        moderator is added as well. The wavelength range is contained in the
        sample description, but needed by the moderator, this transfer is
        also performed in this method.

        Parameters
        ----------

        sample_dimensions : list of length 2
            The width and height parameter for sample dimensions in a list
        """

        reference = "ABSOLUTE"
        for element, next_element in zip(self.guide_elements[:-1], self.guide_elements[1:]):
            element.reference_component_name = reference
            reference = element.end_component_name
            element.set_end_dimensions(next_element.start_width, next_element.start_height)
            element.add_to_instr()

        last_element = self.guide_elements[-1]
        last_element.reference_component_name = reference
        last_element.set_end_dimensions(sample_dimensions[0], sample_dimensions[1])
        last_element.add_to_instr()

    def write_log_file(self, filename):
        # Start file
        with open(filename, "w") as file:
            file.write("Guide log file from python guide_bot\n")

            for element in self.guide_elements:
                element.write_to_log(file)

    def copy_components(self, destination):
        """
        Copies necessary components to destination
        """
        for element in self.guide_elements:
            required_components = element.copy_components(destination)
            for required_component in required_components:
                self.required_components.add(required_component)

    def __repr__(self):
        """
        Provides a string describing the Guide object
        """
        string = "Guide object: "
        if self.name is not None:
            string += self.name
        string += "\n"
        for element in self.guide_elements:
            string += element.__repr__() + "\n"

        for constraint in self.constraints:
            string += constraint.__repr__() + "\n"

        return string


class Project:
    """
    Main logic for performing a guide_bot run with any number of guides

    This class contains the main logic for performing a guide_bot run, and
    handles the scan over input criteria and loop over all user defined
    guides. It needs a sample object describing the figure of merit for
    the guide optimization, and a moderator object describing the neutron
    source including basic restrictions. New Guide objects can be
    generated by the new_guide method, which can then be customized but are
    still connected to the Project instance. Call the run method to perform
    the optimization.
    """
    def __init__(self, name, sample, moderator, analysis_moderators=None, settings=None):
        """
        Create a new Project from sample and moderator specifications

        The Project object contains the main logic for performing a guide_bot
        run and serves as part of the user interface. New guide objects can be
        generated with the new_guide method, and these can then have guide
        elements added to them to describe the guide geometry. The project
        needs a name which will be used to identify the generated folders.

        Parameters
        ----------

        name : str
            Name of this project

        sample : Sample object
            Sample object describing the figure of merit for optimization

        moderator : Object derived from BaseSource
            Description of neutron source used for optimization

        analysis_moderators : list of objects derived from BaseSource
            Description of neutron sources on which the guide will be analyzed

        settings: dict
            Dictionary of settings applicable for simulation / optimization
        """
        self.name = name
        self.base_folder = None

        self.sample = sample
        self.moderator = moderator

        self.guides = []

        source_names = [self.moderator.get_name()]

        if analysis_moderators is None:
            analysis_moderators = []
        elif not isinstance(analysis_moderators, list):
            analysis_moderators = [analysis_moderators]
        self.analysis_moderators = analysis_moderators

        for analysis_moderator in analysis_moderators:
            parameters = analysis_moderator.parameters
            if parameters.get_n_scanned_parameters() > 0:
                raise RuntimeError("Source instances used for analysis can not have scanned parameters!")

            analysis_moderator.make_name_unique(source_names)
            source_names.append(analysis_moderator.get_name())

        if settings is None:
            self.settings = {}
        else:
            self.settings = settings

    def add_guide(self, guide):
        """
        Adds a Guide object to the Project for subsequent optimization

        Parameters
        ----------

        guide : Guide
            Guide object to be added to the Project
        """
        for element in guide.guide_elements:
            element.set_owner("User")

        self.guides.append(guide)

    def new_guide(self, *args, **kwargs):
        """
        Generates and registers a Guide object that will be optimized

        The returned guide object can be expanded by the user to describe the
        desired guide geometry, and does not need to be added to the
        Project object as it is already registered.

        Returns
        -------

        Guide
            Guide object which is expanded by adding GuideElemenets
        """
        new_guide = Guide(*args, **kwargs)
        new_guide.set_current_owner("User")
        self.add_guide(new_guide)

        return new_guide

    def __repr__(self):
        """
        Prints status of Projectrun object

        Returns
        -------

        str
            String with description of status
        """

        string = "guide_bot Project named '" + self.name + "'\n"

        string += "Included guides: \n"
        for guide in self.guides:
            string += "  " + guide.name + "\n"

        mod_scan_shape = self.moderator.parameters.get_scan_shape()
        n_mod_configs = 1
        for dim in mod_scan_shape:
            n_mod_configs *= dim

        string += "Moderator scan configurations: " + str(n_mod_configs) + "\n"

        sample_scan_shape = self.sample.parameters.get_scan_shape()
        n_sample_configs = 1
        for dim in sample_scan_shape:
            n_sample_configs *= dim

        string += "Sample scan configurations: " + str(n_sample_configs) + "\n"

        total_configs = n_sample_configs*n_mod_configs*len(self.guides)
        string += "Total optimizations to be performed: " + str(total_configs) + "\n"

        return string

    def package_single(self, guide, scan_name):
        """
        Saves information needed to perform the guide optimization

        Each guide optimization is prepared as a package saved with dill ready
        to be executed by the guide_bot runner. A package contains a snapshot
        of the moderator and sample used for optimization, each of which has
        their state for this step of the overall scan internalized. The guide
        provided by the user is included, along with all moderators used for
        analysis of additional sources.

        Parameters
        ----------

        guide : Guide
            Guide object which will be expanded with source and sample

        scan_name : str
            Current name for this scan step
        """
        # set up name for this combination
        print(scan_name)

        guide.restore_original()

        if "ncount" not in self.settings:
            self.settings["ncount"] = 1E6

        if "swarmsize" not in self.settings:
            self.settings["swarmsize"] = 25

        if "omega" not in self.settings:
            self.settings["omega"] = 0.5

        if "phip" not in self.settings:
            self.settings["phip"] = 0.5

        if "phig" not in self.settings:
            self.settings["phig"] = 0.5

        if "maxiter" not in self.settings:
            self.settings["maxiter"] = 300

        if "minstep" not in self.settings:
            self.settings["minstep"] = 1E-4

        if "minfunc" not in self.settings:
            self.settings["minfunc"] = 1E-8

        if "logfile" not in self.settings:
            self.settings["logfile"] = True

        self.settings["optimized_monitor"] = "fom.dat"
        self.settings["foldername"] = "optimization_data"

        # Save with dill
        package = {"scan_name": scan_name, "guide": guide, "settings": self.settings,
                   "sample": self.sample, "moderator": self.moderator,
                   "analysis_moderators": self.analysis_moderators,
                   "required_components": guide.required_components}
        outfile = open(scan_name + ".plk", "wb")
        dill.dump(package, outfile)
        outfile.close()

    def write(self, cluster=None):
        """
        Saves optimization job packages for all input configurations

        The write method calls the package_single method for each guide and scans
        over all the input configurations from moderator and sample.
        Writes an overview yaml file describing the project which will aid in
        plotting an overview of the results.
        """
        scan = rpars.InputConfigurationIterator(self.sample, self.moderator)

        # Create new folder for project
        try:
            os.mkdir(self.name)
        except OSError:
            raise RuntimeError("Could not create folder for guide_bot project!")
        self.original_wd = os.getcwd()
        self.base_folder = os.path.join(self.original_wd, self.name)

        if cluster is not None:
            cluster.set_project_path(self.base_folder)
            cluster.read_configuration()
            cluster.start_launch_script()

        guide_names = []
        for guide in self.guides:
        
            guide_names.append(guide.make_name_unique(guide_names))
        
            # Create folder
            print("Now running for guide named ", guide.name)
            
            guide.save_original()

            os.chdir(self.base_folder)
            guide_folder = os.path.join(self.base_folder, guide.name)
            try:
                os.mkdir(guide_folder)
            except OSError:
                raise RuntimeError("Could not create folder for guide!" + guide_folder)

            guide.copy_components(guide_folder)
            os.chdir(guide_folder)

            scan.reset_configuration()
            while scan.next_state():
                # Run each configuration
                scan_name = guide.name + scan.state_string()
                self.package_single(guide, scan_name)

                if cluster is not None:
                    cluster.write_task(foldername=guide.name, scan_name=scan_name)

        os.chdir(self.base_folder)

        # Write overview file
        moderator = {"moderator_name": self.moderator.get_name(),
                     "moderator_fixed": scan.moderator_parameters.get_fixed_dict(),
                     "moderator_scan": scan.moderator_parameters.get_scan_dict(),
                     "moderator_units": scan.moderator_parameters.get_unit_dict()}

        sample = {"sample_name": type(self.sample).__name__,
                  "sample_fixed": scan.sample_parameters.get_fixed_dict(),
                  "sample_scan": scan.sample_parameters.get_scan_dict(),
                  "sample_units": scan.sample_parameters.get_unit_dict()}

        analysis_moderators = {}
        for mod in self.analysis_moderators:
            mod_name = mod.get_name()
            analysis_moderators[mod_name] = {}
            analysis_moderators[mod_name]["parameters"] = mod.parameters.get_fixed_dict()
            analysis_moderators[mod_name]["units"] = mod.parameters.get_unit_dict()

        scan_states = []
        scan.reset_configuration()
        while scan.next_state():
            state_info = {"scan_state": scan.state_string(),
                          "sample_scan": scan.get_sample_state_dict(),
                          "moderator_scan": scan.get_moderator_state_dict()}

            scan_states.append(state_info)

        overview = {"guide_bot_version": __version__,
                    "guide_names": guide_names,
                    "sample": sample,
                    "moderator": moderator,
                    "analysis_moderators": analysis_moderators,
                    "scan_states": scan_states}

        with open("run_overview.yaml", 'w') as yaml_file:
            yaml.dump(overview, yaml_file, default_flow_style=False)

        os.chdir(self.original_wd)

