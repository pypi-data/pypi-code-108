from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.commons.state.parameters_reader import SystemParametersReader


class EnergyPlotting:

    LINKS: str = 'LINKS'
    VALUES: str = 'VALUES'

    # Component types
    GRID: str = 'Grid'
    TRANSFORMER: str = 'Transformer'
    AUXILIARY: str = 'Auxiliary System(s)'
    ACDC_CONVERTER: str = 'ACDC Converter(s)'
    DCDC_CONVERTER: str = 'DCDC Converter(s)'
    STORAGE_TECHNOLOGY: str = 'Storage Technology(-ies)'
    INITIAL_ENERGY_CONTENT: str = 'Initial Energy Content'
    FINAL_ENERGY_CONTENT: str = 'Final Energy Content'

    # Loss categories
    LOSSES: str = ' Losses'

    # Energy flow
    CHARGING: str = ' (ch)'
    DISCHARGING: str = ' (dch)'
    COMPONENTS_CH: str = 'COMPONENTS_CH'
    COMPONENTS_DCH: str = 'COMPONENTS_DCH'
    LOSSES_CH: str = 'Charging Losses'
    LOSSES_DCH: str = 'Discharging Losses'

    COLORS_DICT: dict = {GRID: Plotting.Color.BROWN,
                         TRANSFORMER: Plotting.Color.YELLOW,
                         AUXILIARY: Plotting.Color.BLUE,
                         ACDC_CONVERTER: Plotting.Color.CYAN,
                         DCDC_CONVERTER: Plotting.Color.VIOLET,
                         STORAGE_TECHNOLOGY: Plotting.Color.BRIGHT_GREEN,
                         INITIAL_ENERGY_CONTENT: Plotting.Color.BRIGHT_BLUE,
                         FINAL_ENERGY_CONTENT: Plotting.Color.BRIGHT_BLUE,
                         LOSSES: Plotting.Color.RED,
                         LINKS: Plotting.Color.GREY}

    def __init__(self, data: SystemData, path: str):
        self.__data = data
        self.__data_id: str = data.id
        self.__system_parameters_reader: SystemParametersReader = SystemParametersReader(path)

    def create_categories(self):
        """
        Creates dynamic labels for all nodes/categories representing various components and loss categories in the BESS
        :return: Node/category labels for charge/discharge, and losses as dict
        """
        # Current implementation represents one StorageSystemAC
        category_labels = dict()
        labels_components = dict()
        labels_components[self.GRID] = self.GRID
        labels_components[
            self.TRANSFORMER] = self.TRANSFORMER  # Assuming that a transformer is outside StorageSystemAC
        ac_system_id = int(float(self.__data_id))
        ac_system_id_str = str(ac_system_id) + ' '
        if ac_system_id == 0:
            labels_components[self.ACDC_CONVERTER] = self.ACDC_CONVERTER
            labels_components[self.AUXILIARY] = self.AUXILIARY
            labels_components[self.DCDC_CONVERTER] = self.DCDC_CONVERTER
            labels_components[self.STORAGE_TECHNOLOGY] = self.STORAGE_TECHNOLOGY
        else:
            labels_components[
                self.ACDC_CONVERTER] = ac_system_id_str + self.__system_parameters_reader.get_acdc_converter_type_for(
                ac_system_id)
            auxiliaries = ''
            for aux in self.__system_parameters_reader.get_auxiliaries_for(ac_system_id):
                auxiliaries += aux + ' '
            labels_components[self.AUXILIARY] = ac_system_id_str + auxiliaries

            number_dc_systems: int = self.__system_parameters_reader.get_number_of_storage_systems_dc(ac_system_id)
            dc_idx = 1
            dcdc_converters = ''
            storage_technologies = ''
            while dc_idx <= number_dc_systems:
                dc_system_id_str = str(ac_system_id) + '.' + str(dc_idx) + ' '
                dcdc_converters += dc_system_id_str + self.__system_parameters_reader.get_dcdc_converter_type_for(ac_system_id, dc_idx) + ' '
                storage_technologies += dc_system_id_str + self.__system_parameters_reader.get_storage_technology_for(
                    ac_system_id, dc_idx) + ' '
                dc_idx += 1
            labels_components[self.DCDC_CONVERTER] = dcdc_converters
            labels_components[self.STORAGE_TECHNOLOGY] = storage_technologies

        category_labels[self.COMPONENTS_CH] = {k: v + self.CHARGING for k, v in labels_components.items()}
        category_labels[self.COMPONENTS_CH][self.INITIAL_ENERGY_CONTENT] = self.INITIAL_ENERGY_CONTENT
        category_labels[self.COMPONENTS_CH][self.FINAL_ENERGY_CONTENT] = self.FINAL_ENERGY_CONTENT

        category_labels[self.COMPONENTS_DCH] = {k: v + self.DISCHARGING for k, v in labels_components.items()}

        category_labels[self.LOSSES_CH] = {k: v + self.LOSSES + self.CHARGING for k, v in labels_components.items()}
        category_labels[self.LOSSES_DCH] = {k: v + self.LOSSES + self.DISCHARGING for k, v in
                                            labels_components.items()}
        return category_labels

    def get_data(self) -> SystemData:
        return self.__data

    def get_data_id(self) -> str:
        return self.__data_id

    def system_parameters_reader(self) -> SystemParametersReader:
        return self.__system_parameters_reader
