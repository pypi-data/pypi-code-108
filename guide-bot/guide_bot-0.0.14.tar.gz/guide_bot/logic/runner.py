import copy
import os
import dill
import shutil

from guide_bot.parameters import instrument_parameters as ipars
from guide_bot.parameters import instrument_parameter_container as ipars_container
from guide_bot.logic import length_system
from guide_bot.optimizer import optimizer

from mcstasscript.interface import instr, plotter, functions


class RunFromFile:
    """
    Manages process of combining a user defined Guide object with the
    provided figure of merit and source, create the instrument object and
    perform the numerical optimization. The length system is used to
    parametrize the length and start points, providing a lower number of
    variables due to the overall constraint of a total instrument length
    and internal constraints. When this method is invoked, the moderator
    and sample objects on guide_bot_run are managed, so their values are
    set to the current scan point.
    """

    def __init__(self, filename, settings=None):
        # open package
        infile = open(filename, "rb")
        package = dill.load(infile)
        infile.close()

        # unpack to usual parameter names
        self.scan_name = package["scan_name"]
        self.guide = package["guide"]
        self.settings = package["settings"]
        self.moderator = package["moderator"]
        self.analysis_moderators = package["analysis_moderators"]
        self.sample = package["sample"]
        self.required_components = package["required_components"]

        if settings is not None:
            # Allows easy update of any settings for cluster runs
            self.settings.update(settings)

        self.instrument = None
        self.optimized_parameters = None

        self.guide.restore_original()

        instr_parameters = ipars_container.InstrumentParameterContainer()
        instrument = self.create_instrument(self.moderator, instr_parameters, optimization_mode=True)

        print("debug print")
        print(instr_parameters)

        self.guide.write_log_file(self.scan_name + ".guide_log")

        foldername = self.scan_name + "_optimization"
        self.create_folder(foldername)
        self.settings["foldername"] = os.path.join(foldername, "data")
        best_x = optimizer.run_optimizer(instrument, instr_parameters, self.settings, self.scan_name)
        instr_parameters.set_values(best_x)

        # optimized_parameters = instr_parameters.extract_instrument_parameters(best_x)

        self.analysis_moderators = [self.moderator] + self.analysis_moderators
        for analysis_moderator in self.analysis_moderators:
            self.perform_analysis(analysis_moderator, instr_parameters)

    def perform_analysis(self, analysis_moderator, instr_parameters):
        # Generate folder for results
        analysis_name = self.scan_name + "_" + analysis_moderator.get_name()

        self.create_folder(analysis_name)
        base_folder = os.getcwd()

        print("given instr_parameters to perform_analysis")
        print(instr_parameters)

        """
        if analysis_moderator is self.moderator:
            # Same moderator as optimization, reuse parameters
            # instr_parameters.set_values(best_x) # State already set
            # analysis_instr_parameter = instr_parameters
            # analysis_parameters = instr_parameters.extract_instrument_parameters() # state already set

            instrument = self.create_instrument(analysis_moderator, instr_parameters, optimization_mode=False)
            print("instr_parameters after create instrument")
            print(instr_parameters) # THESE HAVE ALL PARAMETERS TWICE! instr_parameters are generated on top of existing!
            print("-"*120)
            analysis_parameters = instr_parameters.extract_instrument_parameters()
        else:
            # New moderator, perform optimization of free parameters connected to the moderator

            # Start new parameter container
            partial_instr_parameter = ipars_container.InstrumentParameterContainer()

            # Recreate instrument with new parameters
            instrument = self.create_instrument(analysis_moderator, partial_instr_parameter, optimization_mode=True)

            # Lock all parameters with a category not called moderator
            partial_instr_parameter.fix_free_parameters(instr_parameters, exclude="moderator")

            # Perform optimization in case the new moderator have free parameters
            foldername = analysis_name + "_optimization"
            self.create_folder(foldername)
            self.settings["foldername"] = os.path.join(foldername, "optimization")

            best_x_analysis = optimizer.run_optimizer(instrument, partial_instr_parameter, self.settings)
            partial_instr_parameter.set_values(best_x_analysis)
            analysis_parameters = partial_instr_parameter.extract_instrument_parameters(best_x_analysis)

            # Recreate instrument in analysis mode and new parameters
            analysis_instr_parameter = ipars_container.InstrumentParameterContainer()
            instrument = self.create_instrument(analysis_moderator, analysis_instr_parameter, optimization_mode=False)
            analysis_instr_parameter.fix_free_parameters(instr_parameters, exclude="moderator")
            analysis_instr_parameter.set_values(best_x_analysis)
            analysis_parameters = partial_instr_parameter.extract_instrument_parameters(best_x_analysis)
        """

        # Start new parameter container
        partial_instr_parameter = ipars_container.InstrumentParameterContainer()

        # Recreate instrument with new parameters
        instrument = self.create_instrument(analysis_moderator, partial_instr_parameter, optimization_mode=True)

        if analysis_moderator is self.moderator:
            # Lock all parameters
            partial_instr_parameter.fix_free_parameters(instr_parameters)
        else:
            # Lock all parameters with a category not called moderator
            partial_instr_parameter.fix_free_parameters(instr_parameters, exclude="moderator")

        # Perform optimization in case new free parameters are added
        foldername = analysis_name + "_optimization"
        self.create_folder(foldername)
        self.settings["foldername"] = os.path.join(foldername, "optimization")

        best_x_analysis = optimizer.run_optimizer(instrument, partial_instr_parameter, self.settings, self.scan_name)
        partial_instr_parameter.set_values(best_x_analysis)
        #analysis_parameters = partial_instr_parameter.extract_instrument_parameters(best_x_analysis)

        # Recreate instrument in analysis mode and new parameters
        analysis_instr_parameter = ipars_container.InstrumentParameterContainer()
        instrument = self.create_instrument(analysis_moderator, analysis_instr_parameter, optimization_mode=False)

        if analysis_moderator is self.moderator:
            # Lock all parameters
            analysis_instr_parameter.fix_free_parameters(instr_parameters)
        else:
            # Lock all parameters with a category not called moderator
            analysis_instr_parameter.fix_free_parameters(instr_parameters, exclude="moderator")

        analysis_instr_parameter.set_values(best_x_analysis)
        analysis_parameters = partial_instr_parameter.extract_instrument_parameters(best_x_analysis)

        os.chdir(analysis_name)
        dummy = ipars_container.InstrumentParameterContainer()
        instrument_brill_ref = analysis_moderator.create_brilliance_reference_instrument(self.scan_name, dummy, self.sample)

        print("Performing analysis with following parameters:")
        print(analysis_parameters)
        print("Running sample.perform_analysis")

        self.sample.perform_analysis(instrument, instrument_brill_ref, analysis_parameters, self.settings)
        os.chdir(base_folder)

    def create_folder(self, foldername):
        try:
            os.mkdir(foldername)
        except OSError:
            raise RuntimeError("Could not create folder for optimization data! " + foldername)

        current_folder = os.getcwd()
        for file_name in self.required_components:
            origin = os.path.join(current_folder, file_name)
            destination = os.path.join(current_folder, foldername, file_name)

            shutil.copyfile(origin, destination)

    def create_instrument(self, moderator, instr_parameters, optimization_mode=True):

        self.guide.restore_original()

        instr_parameters.set_current_category("moderator")
        self.guide.set_current_owner("moderator")
        moderator.apply_guide_start(self.guide)
        moderator.add_start(self.guide, instr_parameters)

        instr_parameters.set_current_category("sample")
        self.guide.set_current_owner("sample")
        self.sample.add_end(self.guide, instr_parameters)
        self.guide.transfer_end_specifications()

        self.guide.set_current_owner(None)  # Reset current owner of guide

        instr_parameters.set_current_category("length_system")
        length_system.length_system(self.guide.guide_elements, self.sample["instrument_length"], instr_parameters)

        # Start the instrument object
        instrument = instr.McStas_instr(self.scan_name)
        instrument.add_component("Origin", "Progress_bar")

        # Inform all guide elements of the instrument and instrument parameters
        instr_parameters.set_current_category("guide")
        self.guide.set_instrument_and_instr_parameters(instrument, instr_parameters)

        # Before adding source, the sample needs to set wavelength range
        instr_parameters.set_current_category("sample")
        self.sample.add_sample_info(instr_parameters)

        # Add guide system to the instrument
        instr_parameters.set_current_category("guide")
        self.guide.add_to_instrument(self.sample.get_size_parameters())

        # Add source to the instrument
        instr_parameters.set_current_category("moderator")
        moderator.add_to_instrument(instrument, instr_parameters, self.guide.guide_elements[0])

        # Add sample to the instrument
        instr_parameters.set_current_category("sample")
        if optimization_mode:
            self.sample.add_to_instrument(instrument, instr_parameters)
        else:
            self.sample.add_analysis_to_instrument(instrument, instr_parameters)
            self.sample.add_brilliance_analysis_to_instrument(instrument, instr_parameters)



        instr_parameters.set_current_category(None) # Disable category system
        # Export the instrument parameters to the instrument to become parameters
        instr_parameters.export_to_instrument(instrument)

        print("Info on created instrument")
        instrument.print_components()
        instrument.show_parameters()

        return instrument

    def create_brill_ref_instrument(self, moderator, instr_parameters):

        # Start the instrument object
        instrument = instr.McStas_instr(self.scan_name + "_brill_ref")
        instrument.add_component("Origin", "Progress_bar")

        # Add source to the instrument
        instr_parameters.set_current_category("moderator")
        moderator.add_to_instrument(instrument, instr_parameters, self.guide.guide_elements[0])

        instr_parameters.set_current_category("brilliance")
        self.sample.add_brilliance_analysis_to_instrument(instrument, instr_parameters)

        instr_parameters.export_to_instrument(instrument)

        return instrument
