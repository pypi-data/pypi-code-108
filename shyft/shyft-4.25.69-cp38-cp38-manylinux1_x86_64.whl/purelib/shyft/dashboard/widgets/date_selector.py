from typing import Optional, Tuple

import shyft.time_series as sa
from bokeh.layouts import column
from bokeh.models import TextInput, LayoutDOM

from shyft.dashboard.base.app import LayoutComponents, Widget
from shyft.dashboard.base import constants

from shyft.dashboard.base.ports import Sender, Receiver, StatePorts, States

from shyft.dashboard.widgets.logger_box import LoggerBox


class DateSelector(Widget):

    def __init__(self, title: str = '',
                 width: int = 200,
                 height: Optional[int]=None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 max_date: Optional[int] = None,
                 min_date: Optional[int] = None,
                 time_zone: Optional[str] = 'Europe/Oslo',
                 logger: Optional[LoggerBox] = None) -> None:
        super().__init__(logger=logger)

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        self.text_input = TextInput(placeholder='YYYY.MM.DD', title=title, width=width, height=height)
        self.text_input.on_change('value', self._evaluate_date)
        self._set_date = self.update_value_factory(self.text_input, 'value')
        self._layout = column(self.text_input, width=width + padding, height=height, sizing_mode=sizing_mode)
        self.cal = sa.Calendar(time_zone)
        self.current_date_int = None

        self.max_date: int = max_date
        self.min_date: int = min_date

        self.send_selected_date = Sender(parent=self, name='send selected date', signal_type=int)
        self.receive_selected_date = Receiver(parent=self, name='receive selected date', func=self._receive_date,
                                              signal_type=int)
        self.receive_min_date = Receiver(parent=self, name='receive min date', func=self._receive_min_date,
                                         signal_type=int)
        self.receive_max_date = Receiver(parent=self, name='receive max date', func=self._receive_max_date,
                                         signal_type=int)
        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self._state = States.ACTIVE

    @property
    def layout(self) -> LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        """ Property to return all layout.dom components of an visualisation app
            such that they can be arranged by the parent layout obj as
            desired.

            Returns
            -------
            dict
                layout_components as:
                        {'widgets': [],
                         'figures': []}
        """
        return {'widgets': [self.text_input], 'figures': []}

    def _evaluate_date(self, attr, old, new):
        if not new:
            return
        date = self.convert_str_to_date(new)
        error = f"Error: Cannot convert given input date: '{new}' please check format is YYYY.MM.DD and date is vaild"
        date, error = self._evaluate_date_range(date=date)
        if date:
            self._receive_state(States.ACTIVE)
            self.current_date_int = date
            self.send_selected_date(date)
        else:
            self._receive_state(States.INVALID)
            self.logger.error(error)

    def _evaluate_date_range(self, *, date: int) -> Tuple[int, str]:
        date_str = self.convert_date_to_str(date)
        error = ''
        if date and self.max_date:
            if self.max_date < date:
                date = None
                error = f"Error: date: '{date_str}' is larger than max_date '{self.convert_date_to_str(self.max_date)}'"
        if date and self.min_date:
            if self.min_date > date:
                date = None
                error = f"Error: date: '{date_str}' is smaller than min_date '{self.convert_date_to_str(self.min_date)}'"
        return date, error

    def convert_str_to_date(self, date_str: str) -> Optional[int]:
        if date_str.count('.') != 2:
            return None
        yyyy, mm, dd, = date_str.split('.')
        if len(yyyy) != 4 or len(mm) not in [1, 2] or len(dd) not in [1, 2]:
            return None

        def convert_to_int(v):
            try:
                return int(v)
            except ValueError as e:
                return e

        yyyy = convert_to_int(yyyy)
        if not isinstance(yyyy, int):
            return None
        mm = convert_to_int(mm)
        if not isinstance(mm, int):
            return None
        dd = convert_to_int(dd)
        if not isinstance(dd, int):
            return None

        if 0 < mm > 12 or 0 < dd > 31:
            return None
        return self.cal.time(Y=yyyy, M=mm, D=dd)

    def convert_date_to_str(self, date: Optional[int]) -> Optional[str]:
        # noinspection PyBroadException
        try:
            date = int(date)  # allow this to fail, for None '', allow it to succeed for anything convertible to time as int [s]
        except:
            return ''
        u = self.cal.calendar_units(date)
        return f'{u.year}.{u.month}.{u.day}'

    def _receive_date(self, date: int) -> None:
        self.current_date_int, error = self._evaluate_date_range(date=date)
        if error:
            self.logger.error(error)
            self.text_input.value = self.convert_date_to_str(self.current_date_int)
            return
        date_str = self.convert_date_to_str(date)
        self.text_input.value = date_str

    def _receive_min_date(self, date: int) -> None:
        """
        Receive and set the minimum date which can be chosen.

        Parameters
        ----------
        date:
            int epoch time
        """
        self.min_date = date
        if self.current_date_int and self.current_date_int < self.min_date:
            self.current_date_int = self.min_date + self.cal.DAY
            self._set_date(self.convert_date_to_str(self.current_date_int))

    def _receive_max_date(self, date: int) -> None:
        """
        Receive and set the maximum date. The chosen date must be smaller then that

        Parameters
        ----------
        date:
            int epoch time
        """
        self.max_date = date
        if self.current_date_int and self.current_date_int > self.max_date:
            self.current_date_int = self.max_date - self.cal.DAY
            self._set_date(self.convert_date_to_str(self.current_date_int))

    def _receive_state(self, state: States) -> None:
        if state == States.ACTIVE:
            self._state = state
            self.text_input.disabled = False
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self._state = state
            self.text_input.disabled = False
            self.state_port.send_state(state)
        elif state == States.INVALID:
            self._state = state
            self._set_date(self.convert_date_to_str(self.current_date_int))
            self.text_input.disabled = False
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
