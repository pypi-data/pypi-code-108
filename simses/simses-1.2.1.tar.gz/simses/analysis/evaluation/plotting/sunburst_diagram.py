from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.plotting.energy_plotting import EnergyPlotting


class SunburstDiagram(EnergyPlotting):
    """
    SunburstDiagram handles the backend data processing for the sunburst_diagram method of PlotlyPlotting.
    This class dynamically creates labels, parents, and values of energetic quantities as per the
    BESS configuration in SimSES.
    """

    title_extension: str = 'Loss distribution'
    LABELS: str = 'LABELS'
    PARENTS: str = 'PARENTS'

    def __init__(self, data: SystemData, title: str, path: str):
        super().__init__(data, path)
        self.__title = title + self.title_extension
        self.__figures: list = list()

    def create_parameters(self) -> dict:
        """
        Creates parameters (labels, parents, and values) required to plot the Sunburst Diagram which depicts energetic
        quantites such as losses and charged/discharged energy for the BESS
        :param categories: dict of dynamically created energy quantities
        :return: parameters (labels, parents, and values) for the Sunburst Diagram as dict
        """
        categories: dict = self.create_categories()
        data: SystemData = self.get_data()

        labels = list()
        parents = list()
        values = list()

        labels_length = len(labels)

        # Grid (Charging Energy) + Initial Energy Content as first parent
        core_parent_label = categories[self.COMPONENTS_CH][self.GRID] + ' + ' + categories[self.COMPONENTS_CH][self.INITIAL_ENERGY_CONTENT]
        labels.append(core_parent_label)
        values.append(data.charge_energy + data.initial_energy_content)

        # # Initial Energy Content as first parent
        # labels.append(categories[self.COMPONENTS_CH][self.INITIAL_ENERGY_CONTENT])
        # values.append(data.initial_energy_content)

        labels_length_change = len(labels) - labels_length
        parents.extend(labels_length_change * [""])

        # Grid (Charging Energy) as parent of Grid (Discharging Energy) and Losses (Charging) and Losses (Discharging)
        labels_length = len(labels)
        labels.append(categories[self.COMPONENTS_DCH][self.GRID])
        values.append(data.discharge_energy)
        labels.append(categories[self.COMPONENTS_CH][self.AUXILIARY])
        values.append(data.aux_energy_charging)
        labels.append(categories[self.COMPONENTS_DCH][self.AUXILIARY])
        values.append(data.total_aux_losses_energy - data.aux_energy_charging)
        labels.append(self.LOSSES_CH)
        values.append(0 + data.ac_pe_charging_energy - data.dc_power_charging_energy +
                      data.dc_power_charging_energy - data.dc_power_storage_charging_energy +
                      data.storage_technology_loss_energy/2)
        labels.append(self.LOSSES_DCH)
        values.append(0 + data.total_pe_losses_energy - (
                data.ac_pe_charging_energy - data.dc_power_charging_energy) +
                      abs(data.dc_power_discharging_energy - data.dc_power_storage_discharging_energy) +
                      data.storage_technology_loss_energy/2)
        labels.append(categories[self.COMPONENTS_CH][self.FINAL_ENERGY_CONTENT])
        values.append(data.final_energy_content)


        labels_length_change = len(labels) - labels_length
        parents.extend(labels_length_change * [core_parent_label])

        # Losses (Charging) as parent of component-wise charging losses
        labels_length = len(labels)
        labels.append(categories[self.LOSSES_CH][self.TRANSFORMER])
        values.append(0)
        labels.append(categories[self.LOSSES_CH][self.ACDC_CONVERTER])
        values.append(data.ac_pe_charging_energy - data.dc_power_charging_energy)
        labels.append(categories[self.LOSSES_CH][self.DCDC_CONVERTER])
        values.append(data.dc_power_charging_energy - data.dc_power_storage_charging_energy)
        labels.append(categories[self.LOSSES_CH][self.STORAGE_TECHNOLOGY])
        values.append(data.storage_technology_loss_energy/2)

        labels_length_change = len(labels) - labels_length
        parents.extend(labels_length_change * [self.LOSSES_CH])

        # Losses (Discharging) as parent of component-wise discharging losses
        labels_length = len(labels)
        labels.append(categories[self.LOSSES_DCH][self.TRANSFORMER])
        values.append(0)
        labels.append(categories[self.LOSSES_DCH][self.ACDC_CONVERTER])
        values.append(data.total_pe_losses_energy - (
                data.ac_pe_charging_energy - data.dc_power_charging_energy))
        labels.append(categories[self.LOSSES_DCH][self.DCDC_CONVERTER])
        values.append(abs(data.dc_power_discharging_energy - data.dc_power_storage_discharging_energy))
        labels.append(categories[self.LOSSES_DCH][self.STORAGE_TECHNOLOGY])
        values.append(data.storage_technology_loss_energy/2)

        labels_length_change = len(labels) - labels_length
        parents.extend(labels_length_change * [self.LOSSES_DCH])

        parameters = dict()
        parameters[self.LABELS] = labels
        parameters[self.PARENTS] = parents
        parameters[self.VALUES] = values

        return parameters





