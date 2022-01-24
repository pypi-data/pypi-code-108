from typing import Tuple, NamedTuple, Optional

from bokeh.layouts import column
import bokeh.models
from packaging import version
import bokeh
from shyft.dashboard.base import constants
from shyft.dashboard.base.app import LayoutComponents, Widget
from shyft.dashboard.base.ports import (Sender, Receiver, StatePorts, States)
from shyft.dashboard.widgets.logger_box import LoggerBox


class SliderData(NamedTuple):
    start: int
    end: int
    step: int
    value: int
    callback: bool = False


class RangeSliderData(NamedTuple):
    start: int
    end: int
    step: int
    range: Tuple[float, float]
    callback: bool = False


class SliderSelect(Widget):
    def __init__(self,
                 start: int,
                 step: int,
                 end: int,
                 width: int = 210,
                 height: int = 50,
                 title: str = "slider",
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional[LoggerBox] = None,
                 **kwargs) -> None:
        """
        A slider widget to select a value between two values and send it onward via a port.
        """
        super().__init__(logger=logger)

        sizing_mode = sizing_mode or constants.sizing_mode
        padding = padding or constants.widget_padding

        self._step_size = step
        kwargs['title'] = title
        kwargs['width'] = width
        kwargs['step'] = step
        kwargs['start'] = start
        kwargs['end'] = end
        kwargs['value'] = start
        kwargs['height'] = height
        self.slider = bokeh.models.Slider(**kwargs)
        if version.parse(bokeh.__version__) < version.Version("2.3.0"):
            self.slider.on_change('value_throttled', self.on_change)
        else:
            self.slider.on_change('value', self.on_change)

        self.set_slider_value = self.update_value_factory(self.slider, 'value')
        self._layout = column(self.slider, width=width + padding, height=height, sizing_mode=sizing_mode)

        self.receive_param = Receiver(parent=self, name='receive param', func=self._receive_selected_value,
                                      signal_type=SliderData)
        self.send_slider_value = Sender(parent=self, name='send slider value', signal_type=int)

        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.slider], 'figures': []}

    def on_change(self, attr, old, new):
        """
        send selected value with port
        :param attr:
        :param old:
        :param new:
        :return:
        """
        if new:
            self.send_slider_value(new)

    def _receive_selected_value(self, param: SliderData):
        """
        port function to receive value
        :return:
        """
        self.slider.start = param.start
        self.slider.step = param.step
        self.slider.end = param.end
        if param.callback is True:
            self.slider.value = param.value
            if version.parse(bokeh.__version__) < version.Version("2.3.0"):
                self.slider.value_throttled = param.value
            #else:
            #    self.slider.update(value=param.value)
        elif param.callback is False:
            self.set_slider_value(param.value)

    def _receive_state(self, state: States) -> None:
        if state == self.state:
            return
        if state == States.ACTIVE:
            self.state = state
            self.slider.disabled = False  # .state_ports.receive_state(state)
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.state = state
            self.slider.disabled = True  # .state_ports.receive_state(state)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)


class RangeSliderSelect(Widget):
    def __init__(self,
                 start: int,
                 step: int,
                 end: int,
                 width: int = 210,
                 height: int = 50,
                 title: str = "slider",
                 value: Optional[Tuple[int, int]] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 logger: Optional[LoggerBox] = None,
                 show_value: bool = False,
                 **kwargs) -> None:
        """
        A slider widget to select a range of values between two values and send it onward via a port.
        """
        super().__init__(logger=logger)

        sizing_mode = sizing_mode or constants.sizing_mode
        padding = padding or constants.widget_padding
        value = value or (start, end)

        self._step_size = step
        kwargs['title'] = title
        kwargs['width'] = width
        kwargs['step'] = step
        kwargs['start'] = start
        kwargs['end'] = end
        kwargs['value'] = value
        kwargs['height'] = height
        kwargs['show_value'] = show_value
        self.slider = bokeh.models.RangeSlider(**kwargs)
        if version.parse(bokeh.__version__) < version.Version("2.3.0"):
            self.slider.on_change('value_throttled', self.on_change)
        else:
            self.slider.on_change('value', self.on_change)

        self.set_slider_value = self.update_value_factory(self.slider, 'value')
        self._layout = column(self.slider, width=width + padding, height=height, sizing_mode=sizing_mode)

        self.receive_param = Receiver(parent=self, name='receive param', func=self._receive_selected_value,
                                      signal_type=RangeSliderData)
        self.send_slider_value = Sender(parent=self, name='send slider value', signal_type=Tuple[float, float])

        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    @property
    def layout(self) -> bokeh.models.LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': [self.slider], 'figures': []}

    def on_change(self, attr, old, new):
        """
        send selected value with port
        :param attr:
        :param old:
        :param new:
        :return:
        """
        if new:
            self.send_slider_value(new)

    def _receive_selected_value(self, param: RangeSliderData):
        """
        port function to receive value
        :return:
        """
        self.slider.start = param.start
        self.slider.step = param.step
        self.slider.end = param.end
        if param.callback is True:
            self.slider.value = param.range
            if version.parse(bokeh.__version__) < version.Version("2.3.0"):
                self.slider.value_throttled = param.range
        elif param.callback is False:
            self.set_slider_value(param.range)

    def _receive_state(self, state: States) -> None:
        if state == self.state:
            return
        if state == States.ACTIVE:
            self.state = state
            self.slider.disabled = False  # .state_ports.receive_state(state)
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.state = state
            self.slider.disabled = True  # .state_ports.receive_state(state)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
