# Required packages
import pywanda
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from .wanda_plot import plot, PlotTimeseries, PlotRoute, PlotText
# General keys from the config directory
from wanda_api_parameters.parameters_api import (WKEY_GENERAL, WKEY_MIN, WKEY_MAX, WKEY_SERIES, WKEY_PIPES)


class WandaParameter:
    def __init__(
            self,
            wanda_component: str,
            wanda_property: str,
            value=None,
            output=None,
            fig_number=None,
            plot_number=None,
            legend=None,
            table: bool=False,
            wanda_column: str = None,
            property_dict: dict = None
    ):
        """
        Class that holds the wanda parameters

        Parameters
        ----------
        wanda_component: str
            Component name
        wanda_property: str
            Property of the component to set
        value: str or float, optional
            Value for the wanda property.
        output: type, optional
            Export data to a plot or timeseries
        fig_number: type, optional
            Number of the plot to export to.
        plot_number: type, optional
            Number of the plot to export to.
        legend: type, optional
            Name of the component in the legend.
        table: bool, default: False
            Define if the property we're setting is a table or not.
        wanda_column: str, optional
            Column name of the table
        property_dict: dict, optional
            Additional properties for the plot functions.
        """

        self.wanda_component = wanda_component
        self.wanda_property = wanda_property
        self.wanda_column = wanda_column
        self.value = value
        self.output = output
        self.result = None
        self.fig_number = fig_number
        self.plot_number = plot_number
        self.legend = None
        self.table = table
        self.property_dict = property_dict
        # check if legend is NAN
        if legend == legend:
            self.legend = legend

    def __repr__(self):
        return "Parameter object sets property a:%s of component b:%s with value c:%s" % (self.wanda_property,
                                                                                          self.wanda_component,
                                                                                          str(self.value))

    def set_parameter(self, model: pywanda.WandaModel):
        """
        Set the parameter of the component in the corresponding WANDA model

        Parameters
        ----------
        model: pywanda.WandaModel
            The object containing the wanda model
        """
        if self.value is not None:
            if self.table is False:
                wanda_properties = self.get_properties(model)
                # Only assign existing properties to the WANDA model file.
                for idx_property, wanda_property in enumerate(wanda_properties):
                    if wanda_property is not None:
                        if type(wanda_property) == pywanda.WandaProperty:
                            if wanda_property.get_unit_factor() > 0.0:
                                try:
                                    wanda_property.set_scalar(self.value / wanda_property.get_unit_factor())
                                except TypeError as e:
                                    print(e)
                            else:
                                wanda_property.set_scalar(self.value)
                        else:
                            wanda_property(self.value)
            else:
                # Get table properties.
                wanda_properties = self.get_properties(model)
                # Only assign existing properties to the WANDA model file.
                for wanda_property in wanda_properties:
                    if type(wanda_property.get_table()) == pywanda.WandaTable:
                        if wanda_property.get_unit_factor() > 0.0:
                            wanda_property.get_table().set_float_column(self.wanda_column, [val/wanda_property.get_unit_factor() for val in self.value])
                        else:
                            wanda_property.get_table().set_float_column(self.wanda_column, self.value)


    def get_wanda_property(self, wanda_item: pywanda.WandaItem):
        """
        Get the property of the component in the corresponding WANDA model.

        The metod is able to set default properties for each component, action tables, or disuse status.

        Parameters
        ----------
        wanda_item: pywanda.WandaItem
            The component to get the proeprty for.
        """
        # Try to either obtain the wanda item or set it's property to disuse (independent of upper/lower case)
        if wanda_item.contains_property(self.wanda_property):
            return wanda_item.get_property(self.wanda_property)
        elif self.wanda_property.lower() == "Use action table".lower():
            return wanda_item.set_use_action_table(True)
        elif self.wanda_property.lower() == "Disuse".lower():
            # if self.value is not wanda_item.is_disused():
            if self.value is None:
                self.value = True
            return wanda_item.set_disused(self.value)

    def get_properties(self, model: object):
        """
        Get the properties of the component in the WANDA model

        Parameters
        ----------
        model: pywanda.WandaModel
            A pywanda model object.

        Returns
        -------
        properties: List[pywanda.WandaProp])
            A list containing wanda properties for the selected component.
        """
        # Create blank list
        properties = []
        # Get parameters_api model properties.
        if self.wanda_component.lower() == WKEY_GENERAL.lower():
            properties.append(model.get_property(self.wanda_property))
        elif self.table: # If we are getting a table.
            # See if the model contains the component either based on keyword or component name.
            comps = model.get_components_with_keyword(self.wanda_component)
            if len(comps) != 0:
                for comp in comps:
                    properties.append(self.get_wanda_property(comp))
            else:
                if any([comp for comp in model.get_all_components_str() if comp == self.wanda_component]):
                    comp = model.get_component(self.wanda_component)
                    properties.append(self.get_wanda_property(comp))
            # elif model.component_exists(self.wanda_component):
            #     comp = model.get_component(self.wanda_component)
            #     properties.append(self.get_wanda_property(comp))

            # See if the model contains the node either based on keyword or node name.
            nodes = model.get_nodes_with_keyword(self.wanda_component)
            if len(nodes) != 0:
                for node in nodes:
                    properties.append(self.get_wanda_property(node))
            else:
                if any([node for node in model.get_all_nodes_str() if node == self.wanda_component]):
                    node = model.get_node(self.wanda_component)
                    properties.append(self.get_wanda_property(node))
            # elif model.node_exists(self.wanda_component):
            #     node = model.get_node(self.wanda_component)
            #     properties.append(self.get_wanda_property(node))

            # # See if the model contains the signal line either based on keyword or signal line name.
            sig_lines = model.get_signal_lines_with_keyword(self.wanda_component)
            if len(sig_lines) != 0:
                for sig_line in sig_lines:
                    properties.append(self.get_wanda_property(sig_line))
            elif model.sig_line_exists(self.wanda_component):
                sig_line = model.get_signal_line(self.wanda_component)
                properties.append(self.get_wanda_property(sig_line))
        # Check if the key is in all_pipes and the key is not a keyword
        elif (self.wanda_component.lower() == WKEY_PIPES) and (len(model.get_components_with_keyword(self.wanda_component)) == 0):
            # Retrieve all pipes
            comps = model.get_all_pipes()
            # Add all pipes to the property list
            for comp in comps:
                properties.append(self.get_wanda_property(comp))

        else:
            # See if the model contains the component either based on keyword or component name.
            comps = model.get_components_name_with_keyword(self.wanda_component)
            if len(comps) != 0:
                for comp in comps:
                    properties.append(self.get_wanda_property(model.get_component(comp)))
            else:
                if any([comp for comp in model.get_all_components_str() if comp == self.wanda_component]):
                    comp = model.get_component(self.wanda_component)
                    properties.append(self.get_wanda_property(comp))
            # elif model.component_exists(self.wanda_component):
            #     comp = model.get_component(self.wanda_component)
            #     properties.append(self.get_wanda_property(comp))

            # See if the model contains the node either based on keyword or node name.
            nodes = model.get_node_names_with_keyword(self.wanda_component)
            if len(nodes) != 0:
                for node in nodes:
                    properties.append(self.get_wanda_property(model.get_node(node)))
            else:
                if any([node for node in model.get_all_nodes_str() if node == self.wanda_component]):
                    node = model.get_node(self.wanda_component)
                    properties.append(self.get_wanda_property(node))

            # See if the model contains the signal line either based on keyword or signal line name.
            sig_lines = model.get_signal_lines_with_keyword(self.wanda_component)
            if len(sig_lines) != 0:
                for sig_line in sig_lines:
                    properties.append(self.get_wanda_property(sig_line))
            elif model.sig_line_exists(self.wanda_component):
                sig_line = model.get_signal_line(self.wanda_component)
                properties.append(self.get_wanda_property(sig_line))

        return properties


    def get_result_extreme(self, model: pywanda.WandaModel):
        """
        Get the extremes of the corresponding component in the WANDA model

        Parameters
        ----------
        model: pywanda.WandaModel
            A pywanda model object.

        Returns
        -------
        result: float,
            A value either the min or max of the selected components.
        """
        if self.output is not None:
            wanda_properties = self.get_properties(model)
            if self.output.lower() == WKEY_MIN.lower():
                min_val = []
                for wanda_property in wanda_properties:
                    min_val.append(wanda_property.get_extr_min())
                self.result = min(min_val) * wanda_property.get_unit_factor()
            elif self.output.lower() == WKEY_MAX.lower():
                max_val = []
                for wanda_property in wanda_properties:
                    max_val.append(wanda_property.get_extr_max())
                self.result = max(max_val) * wanda_property.get_unit_factor()
        return self.result

    def get_series(self, model:pywanda.WandaModel):
        """
        Get the series of the component for the slected property of the WANDA model

        Parameters
        ----------
        model: pywanda.WandaModel
            A pywanda model object.

        Results
        -------
        result: list[float]
            A series of floats for the selected property of the component.
        """
        self.result = []
        if self.output is not None:
            if self.output == WKEY_SERIES:
                wanda_properties = self.get_properties(model)
                for wanda_property in wanda_properties:
                    try:
                        series = [
                            x * wanda_property.get_unit_factor() for x in wanda_property.get_series()
                        ]
                    except AttributeError:
                        print('Could not load temporal data for comp {} and property {}.'.format(
                            self.wanda_component,
                            self.wanda_property
                        ))
                        series = [np.NaN]
                    except RuntimeError:
                        print('Could not load temporal data for comp {} and property {}.'.format(
                            self.wanda_component,
                            self.wanda_property
                        ))
                        series = [np.NaN]
                        # if model.get_component(self.wanda_component).is_pipe():
                        #     print('Could not load data from unsteady. However, pipe data at t=0 is loaded.')
                        #     series = [
                        #         x[0] * wanda_property.get_unit_factor() for x in wanda_property.get_series_pipe()
                        #     ]
                        # else:
                        #     print('Could not load data from unsteady.')

                    self.result.append(series)
        return self.result

    def create_graphs(self, model: pywanda.WandaModel):
        """
        Get the graphs of the corresponding WANDA model based on the GitHub repo of the wanda_plot file

        Parameters
        ----------
        model: pywanda.WandaModel
            A pywanda model object.

        """
        # TODO: Replace the keys in the PlotTimeseries class
        with PdfPages(f"Document.pdf") as pdf:
            plot_time = [
                PlotTimeseries(
                    [(self.wanda_component, self.wanda_property, self.wanda_component)],
                    title="test",
                    xlabel="test2",
                    ylabel="test2",
                )
            ]
            plot(
                model,
                plot_time,
                title="test",
                case_title="case_title",
                case_description="case_description",
                proj_number="proj_number",
                section_name="section_name",
                fig_name="fig_name",
            )
            pdf.savefig()
            plt.close()
