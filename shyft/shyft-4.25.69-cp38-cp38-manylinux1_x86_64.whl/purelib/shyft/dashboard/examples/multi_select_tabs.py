from typing import Optional, Dict, Any

from bokeh.layouts import row
from bokeh.models import (Panel,Tabs)

from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.widgets.selector_models import LabelDataSelector
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.selector_views import MultiSelect
from shyft.dashboard.base.app import AppBase


class MultiSelectTabsExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "multi_select_tabs_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        labels_tab_A = ['Bardufoss', 'Innsetvatn', 'Vinje', 'Suldalsvatn']
        labels_tab_B = ['Akersvatn','Botnane', 'Ringedalsvatn']

        # MultiSelectors presented as Tabs
        label_view_A = MultiSelect(title='Series A', width=250, size=7, logger=logger)
        label_presenter_A = SelectorPresenter(name='Presenter A', view=label_view_A, logger=logger)
        label_selector_A = LabelDataSelector(presenter=label_presenter_A, logger=logger)

        label_view_B = MultiSelect(title='Series B', width=250, size=7, logger=logger)
        label_presenter_B = SelectorPresenter(name='Presenter B', view=label_view_B, logger=logger)
        label_selector_B = LabelDataSelector(presenter=label_presenter_B, logger=logger)

        tab_A = Panel(child=row(label_view_A.layout), title='Tab A')
        tab_B = Panel(child=row(label_view_B.layout), title='Tab B')
        tabs = Tabs(tabs=[tab_A, tab_B], width=300)

        label_selector_A.receive_labels(labels_tab_A)
        label_selector_B.receive_labels(labels_tab_B)

        return tabs
