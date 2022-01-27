from typing import Optional, Dict, Any
from bokeh.layouts import column
from bokeh.models import (Button, Panel, Tabs, Row, CheckboxGroup, Toggle)
from shyft.dashboard.base.gate_presenter import GatePresenter
from shyft.dashboard.base.ports import (Receiver, Sender, connect_ports)
from shyft.dashboard.base.gate_model import (SingleGate, AggregatedGate)
from shyft.dashboard.base.app import AppBase
from shyft.dashboard.widgets.logger_box import LoggerBox


class CompGatesExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "comp_gates_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name
        # Define ports
        send_10_port = Sender(parent='send_10', name='send 10 port', signal_type=int)
        send_20_port = Sender(parent='send 20', name='send 20 port', signal_type=int)
        send_30_port = Sender(parent='send_30', name='send 30 port', signal_type=int)
        send_40_port = Sender(parent='send 40', name='send 40 port', signal_type=int)
        send_50_port = Sender(parent='send_50', name='send 50 port', signal_type=int)
        send_60_port = Sender(parent='send_60', name='send 60 port', signal_type=int)
        send_71_port = Sender(parent='send_71', name='send 71 port', signal_type=int)
        send_72_port = Sender(parent='send_72', name='send 72 port', signal_type=int)

        def _receive_int_to_print(number: int) -> None:
            print("received number ", number)
            if logger:
                logger.info(f"received number {number}")

        receive_int_to_print = Receiver(parent='parent', name='print_int',
                                        func=_receive_int_to_print, signal_type=int)

        # create button to start the sending of numbers
        send_numbers_button = Button(label='Send numbers', width=170)
        # add button to the bokeh document

        def trigger_send(event):
            send_10_port(10)
            send_20_port(20)
            send_30_port(30)
            send_40_port(40)
            send_50_port(50)
            send_60_port(60)
            send_71_port(71)
            send_72_port(72)

        send_numbers_button.on_click(trigger_send)

        # --- View: Button ---
        # create view for the gate, for example a button here
        button = Button(label='Activate Gate 10', width=170)
        # add button to the bokeh document

        # We define a gate, which has a use_buffer, i.e it will save the value which is send to it when the gate is closed
        # and when the gate is opened afterwards (on button click), the value from the use_buffer will be send.
        # in addictionclear_buffer_after_send=False, will keep the value in the use_buffer, after the value was send.
        # Such that if the button is cluck once more, the same value is send again!
        # NB: Button View requires that the gate has a use_buffer
        gate10 = SingleGate(sender=send_10_port, receiver=receive_int_to_print, connect_function=connect_ports,
                            buffer=True, clear_buffer_after_send=False)

        button_gate_presenter = GatePresenter(view=button, gates=[gate10])

        # --- View: Tabs ---
        # create view for the gate, for example tabs here
        tab1 = Panel(child=Row(), title="Send 20")
        tab2 = Panel(child=Row(), title="Send 30")
        tabs = Tabs(tabs=[tab1, tab2], width=500)

        # for this gates we set the use_buffer=False, which means the send numbers will not be saved and send when the gate is
        # opened
        gate20 = SingleGate(sender=send_20_port, receiver=receive_int_to_print, connect_function=connect_ports, buffer=False)
        gate30 = SingleGate(sender=send_30_port, receiver=receive_int_to_print, connect_function=connect_ports, buffer=False)

        tabs_gate_presenter = GatePresenter(view=tabs, gates=[gate20, gate30])  # assign 1 gate per tab

        # --- View: RadioButtonGroup, RadioGroup, CheckboxGroup, CheckboxButtonGroup ---
        # create view for gates: one of theses is possible here:
        # try it out! RadioButtonGroup, RadioGroup, CheckboxGroup, CheckboxButtonGroup
        check_box = CheckboxGroup(labels=['Activate Gate 40', 'Activate Gate 50'], active=[])

        # for this gates we set the use_buffer=True, but clear_buffer_after_send on True, thus the use_buffer will be send only once!
        gate40 = SingleGate(sender=send_40_port, receiver=receive_int_to_print, connect_function=connect_ports, buffer=True,
                            clear_buffer_after_send=True)
        gate50 = SingleGate(sender=send_50_port, receiver=receive_int_to_print, connect_function=connect_ports, buffer=True,
                            clear_buffer_after_send=True)

        check_box_presenter = GatePresenter(view=check_box, gates=[gate40, gate50])

        # --- View: Toggle ---
        # create view for the gate, for example a button here
        toggle = Toggle(label='Activate Gate 60', width=170)
        # add button to the bokeh document

        # for this gates we set the use_buffer=False,
        gate60 = SingleGate(sender=send_60_port, receiver=receive_int_to_print, connect_function=connect_ports,
                            buffer=False, clear_buffer_after_send=False)

        toggle_gate_presenter = GatePresenter(view=toggle, gates=[gate60])

        # --- View: Button GateModel: AggregateGate ---
        button2 = Button(label='Activate Gate 71 and 72', width=170)
        # add button to the bokeh document

        # We define a 2 gates
        gate71 = SingleGate(sender=send_71_port, receiver=receive_int_to_print, connect_function=connect_ports,
                            buffer=True, clear_buffer_after_send=False)
        gate72 = SingleGate(sender=send_72_port, receiver=receive_int_to_print, connect_function=connect_ports,
                            buffer=True, clear_buffer_after_send=False)
        aggregated_gate_70 = AggregatedGate(gates=[gate71, gate72])

        agg_gate_presenter = GatePresenter(view=button2, gates=[aggregated_gate_70])

        return column(send_numbers_button, button, tabs, check_box, toggle, button2)
