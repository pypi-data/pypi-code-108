from shyft.dashboard.widgets.sliders import SliderSelect, RangeSliderSelect, SliderData, RangeSliderData
from shyft.dashboard.base.ports import States, Receiver, Sender, connect_ports
from shyft.dashboard.base.app import AppBase
from typing import Tuple, Optional, Dict, Any
from bokeh.layouts import column
from shyft.dashboard.widgets.logger_box import LoggerBox

class SliderSelectorExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "slider_selector_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        def _receive_parameters1(tala: int):
            if tala:
                print(f"Slider: {tala}")
                if logger:
                    logger.info(f"Slider: {tala}")

        def _receive_parameters2(tala: Tuple[float, float]):
            if tala:
                print(f"RangeSlider: {tala}")
                if logger:
                    logger.info(f"Slider: {tala}")

        receive_parameters1 = Receiver(parent='self', name='prent', func=_receive_parameters1, signal_type=int)
        receive_parameters2 = Receiver(parent='self', name='prent', func=_receive_parameters2, signal_type=Tuple[float, float])

        slider_view = SliderSelect(width=300, title="Buffer distance (km)", start=0, step=1, end=50, logger=logger)
        range_slider_view = RangeSliderSelect(width=300, title="Elevation (m)", start=0, step=1, end=2500,
                                              logger=logger)

        send_parameters1 = Sender(parent='parent', name='parameters', signal_type=SliderData)
        send_parameters2 = Sender(parent='parent', name='parameters', signal_type=RangeSliderData)

        connect_ports(send_parameters1, slider_view.receive_param)
        connect_ports(send_parameters2, range_slider_view.receive_param)
        connect_ports(slider_view.send_slider_value, receive_parameters1)
        connect_ports(range_slider_view.send_slider_value, receive_parameters2)

        gogn1 = SliderData(start=0, end=50, step=1, value=5)
        gogn2 = RangeSliderData(start=0, end=2500, step=1, range=(100, 200))

        send_parameters1(gogn1)
        send_parameters2(gogn2)

        return column(slider_view.layout_components['widgets'][0],
                         range_slider_view.layout_components['widgets'][0], width=300)
