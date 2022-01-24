import os

from ..utils.constants import LOGConstants, LoggerSCRIPT, IsommeConstants, UnitsConstants, TransducerConstants


class ISOMMEConverter:
    """ """
    def __init__(self):
        self._unit_list = []
        self._transducer_type_list = []
        self._channel_values = []
        self._channel_codes = []
        self._channel_names = []
        self._year_of_test = ""
        self._name_of_test_object = ""
        self._test_nr = ""
        self._model_info = ""
        self._file_directory = ""
        self._file_name = ""
        self._time_of_first_sample = ""

    def write_ISOMME(self, path_to_dir=None, data=None, dynasaur_definitions=None, logger=None, test=False):
        """

        Args:
          path_to_dir:  (Default value = None)
          data:  (Default value = None)
          dynasaur_definitions:  (Default value = None)
          logger:  (Default value = None)
          test:  (Default value = False)

        Returns:

        """
        self._file_directory = path_to_dir
        if isinstance(self._file_directory, str) and self._file_directory == 'exit':
            return -1
        if not os.path.isdir(self._file_directory):
            logger.emit(LOGConstants.ERROR[0], "File directory doesn't exist.")

        check_path = [True, True, True, True]

        if not test:
            while any(check_path):
                if check_path[0]:
                    self._model_info = input('\033[36m' + LOGConstants.INPUT[0]
                                             + '\033[0m' + '\t' "Please enter if your model is AM50 or 6yo: ")
                    if self._model_info == IsommeConstants.MODEL_AM50 or self._model_info == IsommeConstants.MODEL_6YO:
                        check_path[0] = False
                    else:
                        logger.emit(LOGConstants.ERROR[0], "Model doesn't exist.")
                if check_path[1]:
                    self._year_of_test = input('\033[36m' + LOGConstants.INPUT[
                        0] + '\033[0m' + '\t' "Please enter the year of the test (eg: 2019): ")
                    if len(self._year_of_test) == 4:
                        check_path[1] = False
                    else:
                        logger.emit(LOGConstants.ERROR[0], "Date has the wrong format.")
                if check_path[2]:
                    self._name_of_test_object = input('\033[36m' + LOGConstants.INPUT[
                        0] + '\033[0m' + '\t' "Please enter the name of the test object (e.g Pedestrian Model): ")
                    if self._name_of_test_object != "":
                        check_path[2] = False
                    else:
                        logger.emit(LOGConstants.ERROR[0], "No name entered.")
                if check_path[3]:
                    add_info = input('\033[36m' + LOGConstants.INPUT[
                        0] + '\033[0m' + '\t' "Please enter the model information (e.g FCR_30kph): ")
                    if add_info != "":
                        self._test_nr = add_info + "_" + self._model_info
                        check_path[3] = False
                    else:
                        logger.emit(LOGConstants.ERROR[0], "No test number entered.")
            else:
                self._model_info = IsommeConstants.MODEL_AM50
                self._year_of_test = 2020
                self._name_of_test_object = "Model"
                self._test_nr = "info" + "_" + self._model_info

        identifier_list = [tuple(x.split(":")) if x is not None else (None, None, None) for x in
                           dynasaur_definitions.get_info()]
        identifier_list.insert(0, (IsommeConstants.TIME, None, None))

        check_append = True
        for part_of in data.keys():
            for diagram_name in data[part_of].keys():
                if check_append:
                    self._channel_values.append(data[part_of][diagram_name]["Y"])
                    check_append = False
                self._channel_values.append(data[part_of][diagram_name]["X"])

        self._channel_codes = self.get_channel_codes(identifier_list)
        self._channel_names = self.get_channel_names(identifier_list)

        self._unit_list = self.get_unit_type_list(identifier_list)

        self._transducer_type_list = self.get_transducer_type(self._unit_list)

        self._time_of_first_sample = data[list(data.keys())[0]][list(data[list(data.keys())[0]].keys())[0]]["Y"]
        channel_dict_list = self.get_channel_information_dict()

        nr_of_channels = len(data[list(data.keys())[0]][list(data[list(data.keys())[0]].keys())[0]][
                                 "X"])  # len([channel for channel in channel_values if channel != None])

        self.create_output_directory(self._file_directory)
        channel_summary_dict = self.get_channel_summary_dict(nr_of_channels)
        test_nr_mme_dict = self.get_test_nr_mme_dict()

        logger.emit(LOGConstants.SCRIPT[0],
                    LoggerSCRIPT.print_statements[3] + os.path.join(self._file_directory, self._test_nr, "Channel"))
        self.print_channels(channel_dict_list)

        self.print_channel_summary(channel_summary_dict)

        logger.emit(LOGConstants.SCRIPT[0],
                    LoggerSCRIPT.print_statements[5] + os.path.join(self._file_directory, self._test_nr))
        self.print_mme(test_nr_mme_dict)

    def get_channel_information_dict(self):
        """ """
        channel_dict_list = []

        for i, channel_name in enumerate(self._channel_names):
            nr_of_samples = str(len(self._channel_values[i]))

            channel_dict = {"Test object number": 1, "Name of the channel": channel_name,
                            "Laboratory channel code": IsommeConstants.NO_VALUE,
                            "Customer channel code": IsommeConstants.NO_VALUE,
                            "Channel code": self._channel_codes[i], "Unit": self._unit_list[i],
                            "Reference system": IsommeConstants.NO_VALUE,
                            "Transducer type": self._transducer_type_list[i],
                            "Pre filter type": IsommeConstants.NO_VALUE, "Cut off frequency": IsommeConstants.NO_VALUE,
                            "Channel amplitude class": IsommeConstants.NO_VALUE,
                            "Sampling interval": IsommeConstants.NO_VALUE,
                            "Bit resolution": IsommeConstants.NO_VALUE,
                            "Time of first sample": self._time_of_first_sample,
                            "Number of samples": nr_of_samples}

            channel_dict_list.append(channel_dict)

        return channel_dict_list

    def get_channel_summary_dict(self, nr_of_channels):
        """

        Args:
          nr_of_channels: 

        Returns:

        """
        channel_summary_dict = {"Instrumentation standard": IsommeConstants.INSTUMENTATION_STANDARD,
                                "Number of channels": str(nr_of_channels)}
        for i, channel in enumerate(self._channel_names):
            channel_nr_string = str(i + 1)
            channel_summary_dict["Name of channel " + channel_nr_string.rjust(3, '0')] = self._channel_codes[
                                                                                             i] + " / " + channel

        return channel_summary_dict

    def get_test_nr_mme_dict(self):
        """ """
        mme_dict = {"Data format edition number": "1.6", "Customer name": "Euro NCAP",
                    "Customer test ref number": "1", "Title": "Euro NCAP " + self._year_of_test,
                    "Type of the test": "Pedestrian", "Subtype of the test": "Certification",
                    "Regulation": IsommeConstants.NO_VALUE,
                    "Name of test object 1": self._name_of_test_object,
                    "Class of test object 1": IsommeConstants.NO_VALUE,
                    "Ref. number of test object 1": IsommeConstants.NO_VALUE, "Size": self._model_info}
        return mme_dict

    def get_channel_names(self, identifier_list):
        """

        Args:
          identifier_list: 

        Returns:

        """
        channel_names = []
        for identifier in identifier_list:
            channel_name = ""
            for j, item in enumerate(identifier):
                if j % 3 != 0:
                    if item is not None and item != "":
                        channel_name += item + "_"
            channel_name = channel_name.strip("_")
            channel_names.append(channel_name)
        return channel_names

    def get_unit_type_list(self, identifier_list):
        """

        Args:
          identifier_list: 

        Returns:

        """
        unit_type_list = []
        for identifier in identifier_list:
            if identifier[0] == IsommeConstants.TIME:
                unit_type_list.append(UnitsConstants.MILLISECOND)
            elif identifier[0] == IsommeConstants.CONTACT_FORCE:
                unit_type_list.append(UnitsConstants.KNEWTON)
            elif identifier[0] == IsommeConstants.TRAJECTORY:
                unit_type_list.append(UnitsConstants.MILLIMETER)
            elif identifier[0] == IsommeConstants.HEAD_COG:
                unit_type_list.append("g")
            elif identifier[0] == IsommeConstants.HEAD_COG and identifier[1] == "velocity":
                unit_type_list.append(UnitsConstants.VELOCITY)
            elif identifier[0] == IsommeConstants.ENERGY:
                unit_type_list.append(UnitsConstants.JOULE)
            elif identifier[0] == IsommeConstants.ADDED_MASS:
                unit_type_list.append(UnitsConstants.KILOGRAM)
            elif identifier[0] == IsommeConstants.TIMESTEP:
                unit_type_list.append(UnitsConstants.MILLISECOND)
            elif identifier[0] == IsommeConstants.GV:
                unit_type_list.append(UnitsConstants.MILLIMETER)
            elif identifier[0] == IsommeConstants.ENERGY_HBM:
                unit_type_list.append(UnitsConstants.JOULE)
            else:
                unit_type_list.append(IsommeConstants.NO_VALUE)
        return unit_type_list

    def get_transducer_type(self, unit_list):
        """

        Args:
          unit_list: 

        Returns:

        """
        transducer_type_list = []
        for unit in unit_list:
            if unit == UnitsConstants.MILLIMETER:
                transducer_type_list.append(TransducerConstants.COORDINATE)
            elif unit == UnitsConstants.KNEWTON:
                transducer_type_list.append(TransducerConstants.FORCE)
            elif unit == UnitsConstants.MILLISECOND:
                transducer_type_list.append(TransducerConstants.TIME)
            elif unit == "g":
                transducer_type_list.append(TransducerConstants.ACCELERATION)
            elif unit == UnitsConstants.VELOCITY:
                transducer_type_list.append(TransducerConstants.VELOCITY)
            elif unit == UnitsConstants.JOULE:
                transducer_type_list.append(TransducerConstants.ENERGY)
            elif unit == UnitsConstants.KILOGRAM:
                transducer_type_list.append(TransducerConstants.MASS)
            elif unit == "%":
                transducer_type_list.append(TransducerConstants.MASS)
            else:
                transducer_type_list.append(IsommeConstants.NO_VALUE)
        return transducer_type_list

    def get_channel_codes(self, header_info):
        """

        Args:
          header_info: 

        Returns:

        """
        channel_code = []
        if self._model_info == IsommeConstants.MODEL_6YO:
            for i, info in enumerate(header_info):
                ###############TIME##################
                if info[0] == IsommeConstants.TIME:
                    channel_code.append("??TIRS??????TI?0")
                ###############COORDINATES/TRAJECTORIES##################
                elif info[1] == IsommeConstants.HC and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??HEADHC00V6COX0")
                elif info[1] == IsommeConstants.HC and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??HEADHC00V6COZ0")
                elif info[1] == IsommeConstants.C7 and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??CESP0700V6COX0")
                elif info[1] == IsommeConstants.C7 and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??CESP0700V6COZ0")
                elif info[1] == IsommeConstants.T12 and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??THSP1200V6COX0")
                elif info[1] == IsommeConstants.T12 and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??THSP1200V6COZ0")
                elif info[1] == IsommeConstants.AC and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??ACTBAC00V6COX0")
                elif info[1] == IsommeConstants.AC and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??ACTBAC00V6COZ0")
                elif info[1] == IsommeConstants.T8 and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??THSP0800V6COX0")
                elif info[1] == IsommeConstants.T8 and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??THSP0800V6COZ0")
                elif info[1] == IsommeConstants.FER and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??FEMRFR00V6COX0")
                elif info[1] == IsommeConstants.FER and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??FEMRFR00V6COZ0")
                elif info[1] == IsommeConstants.MR and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??ANKLMR00V6COX0")
                elif info[1] == IsommeConstants.MR and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??ANKLMR00V6COZ0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??FEMRFL00V6COX0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??FEMRFL00V6COZ0")
                elif info[1] == IsommeConstants.ML and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??ANKLML00V6COX0")
                elif info[1] == IsommeConstants.ML and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??ANKLML00V6COZ0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??FEMRFEL00V6COX0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??FEMRFEL00V6COZ0")
                ###############RESULTANTS##################
                elif info[1] == IsommeConstants.PEDESTRIAN_GV and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10VEHCSU00V6FOR0")
                elif info[1] == IsommeConstants.HEAD_GV and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10HEAD0700V6FOR0")
                elif info[1] == IsommeConstants.ARM_GV and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10VEHC4500V6FOR0")
                elif info[1] == IsommeConstants.RIGHT_LEG_BUMPER and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10BUMP0200V6FOR0")
                elif info[1] == IsommeConstants.TORSO_BUMPER and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10BUMP0700V6FOR0")
                elif info[1] == IsommeConstants.PEDESTRIAN_BUMPER and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10BUMPSU00V6FOR0")
                elif info[1] == IsommeConstants.PEDESTRIAN_BONNET and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10HOODSU00V6FOR0")
                ###############Energies##################
                elif info[1] == "" and info[2] == IsommeConstants.TOTAL_HOURGLASS_ENERGY:
                    channel_code.append("00EHOUSU00V6EN00")
                elif info[1] == "" and info[2] == IsommeConstants.TOTAL_INTERNAL_ENERGY:
                    channel_code.append("00EINTSU00V6EN00")
                elif info[1] == "" and info[2] == IsommeConstants.TOTAL_ENERGY:
                    channel_code.append("00ETOTSU00V6EN00")
                elif info[1] == "" and info[2] == IsommeConstants.CONTACT_ENERGY:
                    channel_code.append("00ESLISU00V6EN00")
                ###############HEAD COG##################
                elif info[1] == "" and info[2] == IsommeConstants.Z_ACCELERATION:
                    channel_code.append("??HEADHC00V6ACZ0")
                elif info[1] == "" and info[2] == IsommeConstants.RESULTANT_ACCELERATION:
                    channel_code.append("??HEADHC00V6ACR0")
                elif info[1] == "" and info[2] == IsommeConstants.RESULTANT_VELOCITY:
                    channel_code.append("??HEADHC00V6VER0")
                ###############MASS##################
                elif info[1] == IsommeConstants.ADDED_MASS_WS and info[2] == IsommeConstants.WHOLE_SETUP:
                    channel_code.append("00MINCSU00V6MA00")
                elif info[1] == IsommeConstants.REL_ADDED_MASS_WS and info[2] == IsommeConstants.WHOLE_SETUP:
                    channel_code.append("00MINCSU00V6SE00")
                ###############TIMESTEP##################
                elif info[0] == IsommeConstants.TIMESTEP and info[1] == "" and info[2] == "":
                    channel_code.append("00DTIMSU00V6TI00")
                ###############GV##################
                elif info[0] == IsommeConstants.GV and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("10VEHCCG00V6CO00")
                ###############TOTAL HOURGLASS ENERGY HBM##################
                elif info[1] == IsommeConstants.TOTAL_HOURGLASS_ENERGY_HBM and info[2] == "":
                    channel_code.append("??EHOUSU00V6EN00")
                ###############ADDED MASS HBM##################
                elif info[1] == IsommeConstants.ADDED_MASS_WS and info[2] == IsommeConstants.HBM:
                    channel_code.append("??MINCSU00V6MA00")
                ###############HIT##################
                elif info[1] == IsommeConstants.HIT or info[2] == IsommeConstants.HIT or info[0] == IsommeConstants.HIT:
                    channel_code.append("??HEAD??DAV6TI?0")
                ###############WAD##################
                elif info[1] == IsommeConstants.WAD or info[2] == IsommeConstants.WAD or info[0] == IsommeConstants.WAD:
                    channel_code.append("??HEAD??DCV6TI?0")
                else:
                    channel_code.append(IsommeConstants.NO_VALUE)
            return channel_code
        elif self._model_info == IsommeConstants.MODEL_AM50:
            for i, info in enumerate(header_info):
                ###############TIME##################
                if info[0] == IsommeConstants.TIME:
                    channel_code.append("??TIRS??????TI?0")
                ###############COORDINATES/TRAJECTORIES##################
                elif info[1] == IsommeConstants.HC and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??HEADHC00VHCOX0")
                elif info[1] == IsommeConstants.HC and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??HEADHC00VHCOZ0")
                elif info[1] == IsommeConstants.C7 and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??CESP0700VHCOX0")
                elif info[1] == IsommeConstants.C7 and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??CESP0700VHCOZ0")
                elif info[1] == IsommeConstants.T12 and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??THSP1200VHCOX0")
                elif info[1] == IsommeConstants.T12 and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??THSP1200VHCOZ0")
                elif info[1] == IsommeConstants.AC and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??ACTBAC00VHCOX0")
                elif info[1] == IsommeConstants.AC and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??ACTBAC00VHCOZ0")
                elif info[1] == IsommeConstants.T8 and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??THSP0800VHCOX0")
                elif info[1] == IsommeConstants.T8 and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??THSP0800VHCOZ0")
                elif info[1] == IsommeConstants.FER and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??FEMRFR00VHCOX0")
                elif info[1] == IsommeConstants.FER and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??FEMRFR00VHCOZ0")
                elif info[1] == IsommeConstants.MR and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??ANKLMR00VHCOX0")
                elif info[1] == IsommeConstants.MR and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??ANKLMR00VHCOZ0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??FEMRFL00VHCOX0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??FEMRFL00VHCOZ0")
                elif info[1] == IsommeConstants.ML and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??ANKLML00VHCOX0")
                elif info[1] == IsommeConstants.ML and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??ANKLML00VHCOZ0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("??FEMRFEL00VHCOX0")
                elif info[1] == IsommeConstants.FEL and info[2] == IsommeConstants.Z_COORDINATE:
                    channel_code.append("??FEMRFEL00VHCOZ0")
                ###############RESULTANTS##################
                elif info[1] == IsommeConstants.PEDESTRIAN_GV and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10VEHCSU00VHFOR0")
                elif info[1] == IsommeConstants.HEAD_GV and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10HEAD0700VHFOR0")
                elif info[1] == IsommeConstants.ARM_GV and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10VEHC4500VHFOR0")
                elif info[1] == IsommeConstants.RIGHT_LEG_BUMPER and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10BUMP0200VHFOR0")
                elif info[1] == IsommeConstants.TORSO_BUMPER and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10BUMP0700VHFOR0")
                elif info[1] == IsommeConstants.PEDESTRIAN_BUMPER and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10BUMPSU00VHFOR0")
                elif info[1] == IsommeConstants.PEDESTRIAN_BONNET and info[2] == IsommeConstants.RESULTANT_CF:
                    channel_code.append("10HOODSU00VHFOR0")
                ###############Energies##################
                elif info[1] == "" and info[2] == IsommeConstants.TOTAL_HOURGLASS_ENERGY:
                    channel_code.append("00EHOUSU00VHEN00")
                elif info[1] == "" and info[2] == IsommeConstants.TOTAL_INTERNAL_ENERGY:
                    channel_code.append("00EINTSU00VHEN00")
                elif info[1] == "" and info[2] == IsommeConstants.TOTAL_ENERGY:
                    channel_code.append("00ETOTSU00VHEN00")
                elif info[1] == "" and info[2] == IsommeConstants.CONTACT_ENERGY:
                    channel_code.append("00ESLISU00VHEN00")
                ###############HEAD COG##################
                elif info[1] == "" and info[2] == IsommeConstants.Z_ACCELERATION:
                    channel_code.append("??HEADHC00VHACZ0")
                elif info[1] == "" and info[2] == IsommeConstants.RESULTANT_ACCELERATION:
                    channel_code.append("??HEADHC00VHACR0")
                elif info[1] == "" and info[2] == IsommeConstants.RESULTANT_VELOCITY:
                    channel_code.append("??HEADHC00VHVER0")
                ###############MASS##################
                elif info[1] == IsommeConstants.ADDED_MASS_WS and info[2] == IsommeConstants.WHOLE_SETUP:
                    channel_code.append("00MINCSU00VHMA00")
                elif info[1] == IsommeConstants.REL_ADDED_MASS_WS and info[2] == IsommeConstants.WHOLE_SETUP:
                    channel_code.append("00MINCSU00VHSE00")
                ###############TIMESTEP##################
                elif info[0] == IsommeConstants.TIMESTEP and info[1] == "" and info[2] == "":
                    channel_code.append("00DTIMSU00VHTI00")
                ###############GV##################
                elif info[0] == IsommeConstants.GV and info[2] == IsommeConstants.X_COORDINATE:
                    channel_code.append("10VEHCCG00VHCO00")
                ###############TOTAL HOURGLASS ENERGY HBM##################
                elif info[1] == IsommeConstants.TOTAL_HOURGLASS_ENERGY_HBM and info[2] == "":
                    channel_code.append("??EHOUSU00VHEN00")
                ###############ADDED MASS HBM##################
                elif info[1] == IsommeConstants.ADDED_MASS_WS and info[2] == IsommeConstants.HBM:
                    channel_code.append("??MINCSU00VHMA00")
                ###############HIT##################
                elif info[1] == IsommeConstants.HIT or info[2] == IsommeConstants.HIT or info[0] == IsommeConstants.HIT:
                    channel_code.append("??HEAD??DAVHTI?0")
                ###############WAD##################
                elif info[1] == IsommeConstants.WAD or info[2] == IsommeConstants.WAD or info[0] == IsommeConstants.WAD:
                    channel_code.append("??HEAD??DCVHTI?0")
                else:
                    channel_code.append(IsommeConstants.NO_VALUE)
            return channel_code
        else:
            return [IsommeConstants.NO_VALUE] * len(header_info)

    def print_channels(self, channel_dict_list):
        """

        Args:
          channel_dict_list: 

        Returns:

        """
        for i, channel_dict in enumerate(channel_dict_list):
            channel_nr_string = str(i + 1)
            path = os.path.join(self._file_directory, self._test_nr, "Channel",
                                self._test_nr + "." + channel_nr_string.rjust(3, '0'))
            with open(path, 'w') as channel_file:
                for key, value in channel_dict.items():
                    nr_whitespaces = 28 - len(key)
                    whitespaces = " " * nr_whitespaces
                    row = key + whitespaces + ":" + str(value)
                    channel_file.write('{}\n'.format(row))
                for value in self._channel_values[i]:
                    channel_file.write('{}\n'.format(value))

    def print_channel_summary(self, channel_summary_dict):
        """

        Args:
          channel_summary_dict: 

        Returns:

        """
        path = os.path.join(self._file_directory, self._test_nr, "Channel", self._test_nr + ".chn")
        with open(path, 'w') as channel_summary_file:
            for key, value in channel_summary_dict.items():
                nr_whitespaces = 28 - len(key)
                whitespaces = " " * nr_whitespaces
                row = key + whitespaces + ":" + value
                channel_summary_file.write('{}\n'.format(row))

    def print_mme(self, mme_dict):
        """

        Args:
          mme_dict: 

        Returns:

        """
        path = os.path.join(self._file_directory, self._test_nr, self._test_nr + ".mme")
        with open(path, 'w') as mme_file:
            for key, value in mme_dict.items():
                nr_whitespaces = 28 - len(key)
                whitespaces = " " * nr_whitespaces
                row = key + whitespaces + ":" + value
                mme_file.write('{}\n'.format(row))

    def create_output_directory(self, output_directory):
        """

        Args:
          output_directory: 

        Returns:

        """
        if not os.path.exists(os.path.join(output_directory, self._test_nr)):
            os.mkdir(os.path.join(output_directory, self._test_nr))
        if not os.path.exists(os.path.join(output_directory, self._test_nr, "Channel")):
            os.mkdir(os.path.join(output_directory, self._test_nr, "Channel"))
