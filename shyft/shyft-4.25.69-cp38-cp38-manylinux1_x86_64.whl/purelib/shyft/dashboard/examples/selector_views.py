from typing import List, Optional, Dict, Any
from shyft.dashboard.base.ports import connect_ports, Receiver
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.selector_views import (TextInput, AutocompleteInput,
                                                 FilterMultiSelect,
                                                 MultiSelect,
                                                 TwoSelect,
                                                 Select,
                                                 CheckboxButtonGroup,
                                                 CheckboxGroup,
                                                 RadioGroup,
                                                 RadioButtonGroup)
from shyft.dashboard.widgets.logger_box import LoggerBox

from shyft.dashboard.widgets.selector_models import LabelDataSelector

from bokeh.io import curdoc
from bokeh.layouts import row, column
from shyft.dashboard.base.app import AppBase


class CompSelectorViewsExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "comp_selector_views_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        # not we need some fruits
        known_fruits = ["Banana", "Apple", "Kiwi", "Dragon Fruit", 'Gava', 'Orange', 'Watermelon', 'Melon']

        # print port to print the selection
        def _receive_selection_to_print(tags: List[str]):
            if tags:
                print("selected fruit(s) ", ', '.join(tags))
                if logger:
                    logger.info("selected fruit(s) ", ', '.join(tags))

        # create print port
        receive_selection_to_print = Receiver(parent='parent', name='print', func=_receive_selection_to_print,
                                              signal_type=List[str])

        # Select
        select_view = Select(title='Fruit select', logger=logger)
        select_presenter = SelectorPresenter(name='Fruits', view=select_view, logger=logger)
        select_selector = LabelDataSelector(presenter=select_presenter, logger=logger)

        # Two Select
        two_select_view = TwoSelect(title='Fruit two select', logger=logger)
        two_select_presenter = SelectorPresenter(name='Fruits', view=two_select_view, logger=logger)
        two_select_selector = LabelDataSelector(presenter=two_select_presenter, logger=logger)

        # Multi Select
        multi_select_view = MultiSelect(title='Fruit select', size=4, logger=logger)
        multi_select_presenter = SelectorPresenter(name='Fruits', view=multi_select_view, logger=logger)
        multi_select_selector = LabelDataSelector(presenter=multi_select_presenter, logger=logger)

        # FilterMulti Select
        filter_multi_select_view = FilterMultiSelect(title='Fruit filter select', size=len(known_fruits), logger=logger)
        filter_multi_select_presenter = SelectorPresenter(name='Fruits', view=filter_multi_select_view, logger=logger)
        filter_multi_select_selector = LabelDataSelector(presenter=filter_multi_select_presenter, logger=logger)

        # Autocomplete Input
        auto_complete_view = AutocompleteInput(title='Fruit autocomplete input',
                                               placeholder="enter fruits name",
                                               logger=logger)
        auto_complete_presenter = SelectorPresenter(name='Fruits', view=auto_complete_view, logger=logger)
        auto_complete_selector = LabelDataSelector(presenter=auto_complete_presenter, logger=logger)

        # Checkbox group
        checkboxgroup_view = CheckboxGroup(title='CheckboxGroup', logger=logger)
        checkboxgroup_presenter = SelectorPresenter(name='CheckboxGroup Labels', view=checkboxgroup_view, logger=logger)
        checkboxgroup_selector = LabelDataSelector(presenter=checkboxgroup_presenter, logger=logger)

        # Checkboxbutton group
        checkbox_button_group_view = CheckboxButtonGroup(title='CheckboxButtonGroup', width=550, logger=logger)
        checkbox_button_group_presenter = SelectorPresenter(name='CheckboxButtonGroup Labels',
                                                            view=checkbox_button_group_view,
                                                            logger=logger)
        checkbox_button_group_selector = LabelDataSelector(presenter=checkbox_button_group_presenter, logger=logger)

        # radio group
        radio_group_view = RadioGroup(title='RadioGroup', logger=logger)
        radio_group_presenter = SelectorPresenter(name='RadioGroup Labels', view=radio_group_view, logger=logger)
        radio_group_selector = LabelDataSelector(presenter=radio_group_presenter, logger=logger)

        # radio button group
        radio_button_group_view = RadioButtonGroup(title='RadioButtonGroup', width=550, logger=logger)
        radio_button_group_presenter = SelectorPresenter(name='RadioGroup Labels',
                                                         view=radio_button_group_view,
                                                         logger=logger)
        radio_button_group_selector = LabelDataSelector(presenter=radio_button_group_presenter, logger=logger)

        # connect console print function to selector model
        connect_ports(select_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(two_select_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(multi_select_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(auto_complete_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(checkboxgroup_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(checkbox_button_group_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(radio_group_selector.send_selected_labels, receive_selection_to_print)
        connect_ports(radio_button_group_selector.send_selected_labels, receive_selection_to_print)

        # fill auto complete input with available tags
        select_selector.receive_labels(known_fruits)
        two_select_selector.receive_labels(known_fruits)
        multi_select_selector.receive_labels(known_fruits)
        filter_multi_select_selector.receive_labels(known_fruits)
        auto_complete_selector.receive_labels(known_fruits)
        checkboxgroup_selector.receive_labels(known_fruits)
        checkbox_button_group_selector.receive_labels(known_fruits)
        radio_group_selector.receive_labels(known_fruits)
        radio_button_group_selector.receive_labels(known_fruits)

        # add views to bokeh document
        return row(row(TextInput().layout, select_view.layout,
                   two_select_view.layout,
                   multi_select_view.layout,
                   filter_multi_select_view.layout,
                   column(auto_complete_view.layout)), row(
                   checkboxgroup_view.layout,
                   checkbox_button_group_view.layout,
                   radio_group_view.layout,
                   radio_button_group_view.layout), spacing=40)

