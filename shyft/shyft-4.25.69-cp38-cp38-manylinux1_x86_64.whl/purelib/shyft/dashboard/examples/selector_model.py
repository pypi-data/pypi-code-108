'''
Example how to implement a data selector model using the SelectorModelBase
'''
from time import sleep
from typing import Dict, List, Tuple, Optional, Any

from shyft.dashboard.base.ports import States, Receiver, Sender, connect_ports
from shyft.dashboard.base.selector_model import processing_wrapper, SelectorModelBase
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.selector_views import TwoSelect
from shyft.dashboard.base.app import AppBase
from shyft.dashboard.widgets.logger_box import LoggerBox


class TimesElevenPlusFiveSelector(SelectorModelBase):
    """
    Simple selector which takes a dom obj: Dict[str, int]

    When a selection is made we want to return a new dom obj whitch contains a new dom obj for all the
    selected entries where the value_new = value_old + 11 * 5.

    In addition since calculating takes long time, we will wait for sleep_time before we send the results.

    This is just for the purpose of ...
    """

    def __init__(self, presenter: SelectorPresenter, sleep_time, logger=None) -> None:
        super().__init__(presenter=presenter, logger=logger)

        # sleep time to simulate tedious loading
        self.sleep_time = sleep_time  # s

        # the current domain model object
        self.current_dom_object = {}

        # add ports for receiving dom and sending selection
        self.receive_dom = Receiver(parent=self, name='receive dom obj', func=self._receive_dom_objects,
                                    signal_type=Dict[str, float])
        self.send_modified_dom = Sender(parent=self, name='send processed dom obj', signal_type=Dict[str, float])

    # --- definition of all abstract methods ---
    def on_change_selected(self, new_values: List[str]):
        # send state information that the state is going to change and deactivate all connected widgets
        self.state_port.send_state(States.DEACTIVE)
        # process selection
        processed_values = self.process_selection_evaluation(new_values)
        if processed_values:
            # update the state of the connected widgets that they are ready to receive the result
            self.state_port.send_state(States.ACTIVE)
            # send the result
            self.send_modified_dom(processed_values)

    # --- definition of the custom processing receiver and sender functions ---
    @processing_wrapper  # decorator @processing_wrapper: changes state of the presentation model, which notifies user
    def process_selection_evaluation(self, new_values: List[str]) -> Dict[str, float]:
        # process what to do with the new value
        processed_values = {n: self.current_dom_object[n] * 11 + 5 for n in new_values if
                            n in self.current_dom_object}
        # mimic a tedious load function we sleep for a while
        sleep(self.sleep_time)
        # return processed value
        return processed_values

    @processing_wrapper  # decorator @processing_wrapper: changes state of the presentation model, which notifies user
    def loading_function(self, new_dom: Dict[str, float]) -> List[Tuple[str, str]]:
        # There are two possibilities for setting up the option list for the presentation model:
        #
        # 1. List[label]: Each drop down element is represented by a label. The value returned by the widget to the
        # on_change_selected callback (below) is equal to the label
        # 2. List[(key, label)]: For each drop down element we create a tuple with 2 strings: (key, label),
        # where label is what you see in the bokeh-widget.
        # Key is the value returned by the widget to the on_change_selected callback (above).
        self.current_dom_object = new_dom
        return [(k, f'{k}: {v}, return {v}*11+5') for k, v in new_dom.items()]

    def _receive_dom_objects(self, dom_obj: Dict[str, float] )  -> None:
        # if the state is not active do nothing
        if self.state == States.DEACTIVE:
            return
        # 1. create option list we want to show on the presentation model
        # here we decide to do this in a loading functions, since we want to use the @processing_wrapper decorator,
        # which changes state of the presentation model, which notifies user
        #
        # In short, options should be of either List[(key, label)] or List[label]
        new_options = self.loading_function(dom_obj)
        # 2. update the selector options without sending the callback function
        self.presenter.set_selector_options(new_options, callback=False, sort=True,
                                            sort_reverse=False, selected_value=None)


class CompSelectorModelExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "comp_selector_model_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        view = TwoSelect(title='Custom select model', logger=logger)
        # create presentation model
        presenter = SelectorPresenter(name="custom presenter", view=view, logger=logger)

        # create our data selector
        selector_model = TimesElevenPlusFiveSelector(presenter=presenter, sleep_time=3, logger=logger)

        # create a dom obj
        dom = {'foo': 214, 'bar': 585, 'foo-bar': 452854, 'bar-foo': 1423}
        # feed in the dom object
        selector_model.receive_dom(dom)

        print(presenter.selector_options)

        # create a port function to print our dom obj to the console
        def _receive_dom_to_print(dom_obj: Dict[str, float]):
            print('\n----------')
            print("  dom object\n")
            if dom_obj:
                for k, v in dom_obj.items():
                    print('  {}:  {}'.format(k, v))
            print('-----------\n')
            if logger:
                logger.info(f' dom object: {"".join(["  {}:  {}".format(k, v) for k, v in dom_obj.items()])}')

        receive_dom_to_print = Receiver(parent=_receive_dom_to_print, name='print dom', func=_receive_dom_to_print,
                                        signal_type=Dict[str, float])

        # connect our function to selector model
        connect_ports(selector_model.send_modified_dom, receive_dom_to_print)

        return view.layout



