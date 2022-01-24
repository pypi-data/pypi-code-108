from typing import List

from shyft.time_series import Calendar, time

from shyft.dashboard.base.ports import Receiver, Sender, States
from shyft.dashboard.base.selector_model import SelectorModelBase
from shyft.dashboard.base.selector_presenter import SelectorPresenter


def dt_to_str(dt: int) -> str:
    ''' Convert dt to a str giving months weeks, days, hours
    '''
    dt = time(dt)
    nYear = dt//Calendar.YEAR
    res = (dt%Calendar.YEAR)
    nMonth = res//Calendar.MONTH
    res = (res%Calendar.MONTH)
    nWeek = res//Calendar.WEEK
    res = (res%Calendar.WEEK)
    nDay = res//Calendar.DAY
    res = (res%Calendar.DAY)
    nHour = res//Calendar.HOUR
    res = (res%Calendar.HOUR)
    nMin = res // Calendar.MINUTE
    res = (res%Calendar.MINUTE)
    nSec = res // 1
    # calc quarter
    nQuarter = nMonth//3
    nMonth = nMonth%3
    counts = [int(nYear), int(nQuarter), int(nMonth), int(nWeek), int(nDay), int(nHour), int(nMin), int(nSec)]
    labels = ['Year', 'Quarter', 'Month', 'Week', 'Day', 'Hour', 'Minute', 'Second']
    ses = ['s' if n > 1 else '' for n in counts]
    return ' '.join([f'{n} {t}{s}' for n, t, s in zip(counts, labels, ses) if n != 0])


class DeltaTSelector(SelectorModelBase):
    def __init__(self, presenter: SelectorPresenter, logger=None) -> None:
        """
        dt selctor model used with TsViewer

        Parameters
        ----------
        presenter: SelectorPresenter instance to use
        logger: optional logger instance
        """
        super(DeltaTSelector, self).__init__(presenter=presenter, logger=logger)
        self.presenter.default = 'Auto'
        self.receive_selection_options = Receiver(parent=self, name='receive dt options',
                                                  func=self._receive_selection_options, signal_type=List[int])
        self.send_dt = Sender(parent=self, name='send dt', signal_type=int)
        self.state = States.DEACTIVE

    def on_change_selected(self, selection_list: List[str]) -> None:
        if self.state == States.DEACTIVE or not selection_list or not selection_list[0]:
            return
        dt = self._convert_selected_dt(selection_list[0])
        self.send_dt(dt)

    @staticmethod
    def _convert_selected_dt(selected_dt: str) -> int:
        if 'Auto' in selected_dt:
            selected_dt = selected_dt.split('Auto: ')[-1]
        return int(selected_dt)

    def _receive_selection_options(self, dt_list: List[int]):
        if not isinstance(dt_list, List):
            self.presenter.set_selector_options(callback=False)
            return
        # generate options
        dt_list = sorted(dt_list)
        options = [(str(int(dt)), dt_to_str(dt)) for dt in dt_list]
        if options:
            self.presenter.default = ('Auto: {}'.format(options[0][0]), 'Auto: {}'.format(options[0][1]))
        else:
            self.presenter.default = 'Auto'

        # selection
        curr_select = None
        if len(dt_list) != 0:
            if not self.presenter.selected_values or not self.presenter.selected_values[0]:
                curr_select = dt_list[0]
            else:
                selected_value = self.presenter.selected_values[0]
                # if Auto
                if 'Auto' in selected_value:
                    if options:
                        curr_select = 'Auto: {}'.format(options[0][0])
                    else:
                        curr_select = None
                # if not Auto
                else:
                    selected_value = int(selected_value)
                    if selected_value in dt_list:
                        curr_select = str(selected_value)
                    else:
                        if dt_list[0] > selected_value:
                            curr_select = str(int(dt_list[0]))
                        elif dt_list[-1] < selected_value:
                            curr_select = str(int(dt_list[-1]))

            self.presenter.set_selector_options(options, sort=False, selected_value=curr_select, callback=False)
        if curr_select:
            self.send_dt(self._convert_selected_dt(curr_select))

    def _receive_state(self, state: States) -> None:
        if state == self.state:
            return
        self.state = state
        if state == States.ACTIVE:
            self.presenter.state_ports.receive_state(state)
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.presenter.default = ('', 'Auto')
            self.presenter.state_ports.receive_state(state)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
