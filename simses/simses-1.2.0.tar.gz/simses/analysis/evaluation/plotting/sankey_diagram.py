from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.plotting.energy_plotting import EnergyPlotting


class SankeyDiagram(EnergyPlotting):
    """
    SankeyDiagram handles the backend data processing for the  sankey_diagram method of PlotlyPlotting.
    This class dynamically creates nodes, sources, targets, and values of flow quantities for the links as per the
    BESS configuration in SimSES.
    The class also creates all node labels and assigns colors to the links and nodes.
    """

    NODE_LABELS: str = 'NODE_LABELS'
    SOURCES: str = 'SOURCES'
    TARGETS: str = 'TARGETS'

    # Node colors
    NODE_COLORS: str = 'NODE_COLORS'
    LINK_COLORS: str = 'LINK_COLORS'

    def __init__(self, data: SystemData, title: str, path: str):
        super().__init__(data, path)
        self.__title = title
        self.__figures: list = list()

    def create_node_links(self) -> dict:
        """
        Creates node links (sources, targets, and values) from provided data and node labels
        :param node_labels: node labels as dict
        :return: link attributes (node labels, node colors, link colors, sources, targets, values) as dict
        """
        node_labels: dict = self.create_categories()
        data: SystemData = self.get_data()

        sources = list()
        targets = list()
        values = list()

        # Charging

        # Grid to Transformer
        sources.append(node_labels[self.COMPONENTS_CH][self.GRID])
        targets.append(node_labels[self.COMPONENTS_CH][self.TRANSFORMER])
        values.append(data.charge_energy)

        # Transformer to losses, Aux, and AC/DC Converter
        sources.append(node_labels[self.COMPONENTS_CH][self.TRANSFORMER])
        targets.append(node_labels[self.LOSSES_CH][self.TRANSFORMER])
        values.append(0)  # Currently transformer implementation is lossless

        sources.append(node_labels[self.COMPONENTS_CH][self.TRANSFORMER])
        targets.append(node_labels[self.COMPONENTS_CH][self.AUXILIARY])
        values.append(data.aux_energy_charging)  # TODO check if segregation is correct

        sources.append(node_labels[self.COMPONENTS_CH][self.TRANSFORMER])
        targets.append(node_labels[self.COMPONENTS_CH][self.ACDC_CONVERTER])
        values.append(data.ac_pe_charging_energy)  # TODO check if segregation is correct

        # AC/DC Converter to losses, DC/DC Converter
        sources.append(node_labels[self.COMPONENTS_CH][self.ACDC_CONVERTER])
        targets.append(node_labels[self.LOSSES_CH][self.ACDC_CONVERTER])
        values.append(
            data.ac_pe_charging_energy - data.dc_power_charging_energy)  # TODO check if value is correct

        sources.append(node_labels[self.COMPONENTS_CH][self.ACDC_CONVERTER])
        targets.append(node_labels[self.COMPONENTS_CH][self.DCDC_CONVERTER])
        values.append(data.dc_power_charging_energy)  # TODO check if value is correct

        # DC/DC Converter to losses, Storage Technology
        sources.append(node_labels[self.COMPONENTS_CH][self.DCDC_CONVERTER])
        targets.append(node_labels[self.LOSSES_CH][self.DCDC_CONVERTER])
        values.append(
            data.dc_power_charging_energy - data.dc_power_storage_charging_energy)  # TODO check if value is correct

        sources.append(node_labels[self.COMPONENTS_CH][self.DCDC_CONVERTER])
        targets.append(node_labels[self.COMPONENTS_CH][self.STORAGE_TECHNOLOGY])
        values.append(data.dc_power_storage_charging_energy)  # TODO check if value is correct

        # Accounting for initial energy content in Storage Technology
        sources.append(node_labels[self.COMPONENTS_CH][self.INITIAL_ENERGY_CONTENT])
        targets.append(node_labels[self.COMPONENTS_CH][self.STORAGE_TECHNOLOGY])
        values.append(data.initial_energy_content)

        # Storage Technology (charging) to Storage Technology losses
        sources.append(node_labels[self.COMPONENTS_CH][self.STORAGE_TECHNOLOGY])
        targets.append(node_labels[self.LOSSES_CH][self.STORAGE_TECHNOLOGY])
        values.append(data.storage_technology_loss_energy)  # TODO check if segregation is correct

        # Accounting for final energy content in Storage Technnology
        sources.append(node_labels[self.COMPONENTS_CH][self.STORAGE_TECHNOLOGY])
        targets.append(node_labels[self.COMPONENTS_CH][self.FINAL_ENERGY_CONTENT])
        values.append(data.final_energy_content)

        # Discharging
        # Storage Technology (charging) to DCDC Converter (Discharging)
        sources.append(node_labels[self.COMPONENTS_CH][self.STORAGE_TECHNOLOGY])
        targets.append(node_labels[self.COMPONENTS_DCH][self.DCDC_CONVERTER])
        values.append(-1 * data.dc_power_storage_discharging_energy)

        # DCDC Converter to losses, ACDC Converter
        sources.append(node_labels[self.COMPONENTS_DCH][self.DCDC_CONVERTER])
        targets.append(node_labels[self.LOSSES_DCH][self.DCDC_CONVERTER])
        values.append(abs(data.dc_power_discharging_energy - data.dc_power_storage_discharging_energy))

        sources.append(node_labels[self.COMPONENTS_DCH][self.DCDC_CONVERTER])
        targets.append(node_labels[self.COMPONENTS_DCH][self.ACDC_CONVERTER])
        values.append(-1 * data.dc_power_discharging_energy)

        # ACDC Converter to losses, Transformer, Aux
        sources.append(node_labels[self.COMPONENTS_DCH][self.ACDC_CONVERTER])
        targets.append(node_labels[self.LOSSES_DCH][self.ACDC_CONVERTER])
        values.append(data.total_pe_losses_energy - (
                data.ac_pe_charging_energy - data.dc_power_charging_energy))  # TODO obtain values

        sources.append(node_labels[self.COMPONENTS_DCH][self.ACDC_CONVERTER])
        targets.append(node_labels[self.COMPONENTS_DCH][self.TRANSFORMER])
        values.append(data.discharge_energy)

        sources.append(node_labels[self.COMPONENTS_DCH][self.ACDC_CONVERTER])
        targets.append(node_labels[self.COMPONENTS_DCH][self.AUXILIARY])
        values.append(data.total_aux_losses_energy - data.aux_energy_charging)  # TODO obtain values

        # Transformer to losses, Grid
        sources.append(node_labels[self.COMPONENTS_DCH][self.TRANSFORMER])
        targets.append(node_labels[self.LOSSES_DCH][self.TRANSFORMER])
        values.append(0)  # Lossless transformer

        sources.append(node_labels[self.COMPONENTS_DCH][self.TRANSFORMER])
        targets.append(node_labels[self.COMPONENTS_DCH][self.GRID])
        values.append(data.discharge_energy)

        # Convert alphabetical connections to index numbers of labels
        labels = list()
        node_colors = list()
        for v in node_labels.values():
            for key in v.keys():
                node_colors.append(self.COLORS_DICT[key])
            for label in v.values():
                labels.append(label)

        source_indices = list()
        for source in sources:
            source_indices.append(labels.index(source))

        target_indices = list()
        link_colors = list()
        for target in targets:
            if self.LOSSES in target:
                link_colors.append(self.COLORS_DICT[self.LOSSES])
            else:
                link_colors.append(self.COLORS_DICT[self.LINKS])
            target_indices.append(labels.index(target))

        links = dict()
        links[self.NODE_LABELS] = labels
        links[self.NODE_COLORS] = node_colors
        links[self.SOURCES] = source_indices
        links[self.TARGETS] = target_indices
        links[self.VALUES] = values
        links[self.LINK_COLORS] = link_colors
        return links
