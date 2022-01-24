
import traits.api as tr
from .editors import EditorFactory
import ipywidgets as ipw

import time
from threading import Thread

class RunSimThread(Thread):
    r'''Thread launcher class used to issue a calculation.
    in an independent thread.
    '''

    def __init__(self, method, model, *args, **kw):
        super(RunSimThread, self).__init__(*args, **kw)
        self.daemon = True
        self.method = method
        self.model = model
    def run(self):
        self.method(self.model)
        return


class ProgressEditor(EditorFactory):
    """
    Progress bar running between 0 and 1 by default
    """
    run_method = tr.Str
    reset_method = tr.Str
    interrupt_var = tr.Str
    time_var = tr.Str
    time_max = tr.Str
    refresh_freq = tr.Float(2)

    #=========================================================================
    # COMPUTATION THREAD
    #=========================================================================
    _run_thread = tr.Instance(RunSimThread)
    _running = tr.Bool(False)

    def run(self, model):
        r'''Run the simulation - can be started either directly or from a thread
        '''
        self._running = True
        try:
            # start the calculation
            run_fn = getattr(model, str(self.run_method))
            run_fn()

        except Exception as e:
            self._running = False
            raise e  # re-raise exception

        self._running = False

    def watch(self, model):
        r"""Watch the loop and update the progress bar
        """
        t = getattr(self.model, self.time_var)
        t_max = getattr(self.model, self.time_max)
        while self._running: # and t <= t_max:
            if (self.interrupt_var is not None) and getattr(self.model, self.interrupt_var):
                break
            time.sleep(1 / self.refresh_freq)
            t = getattr(self.model, self.time_var)
            self.pb.value = t
            self.ui_pane.interactor.update_plot(self.ui_pane.index)
        self.run_button.style.button_color = 'lightgray'
        self.interrupt_button.style.button_color = 'lightgray'
        self.reset_button.style.button_color = 'gray'

    def run_thread(self, model):
        r'''Run a thread if it does not exist - do nothing otherwise
        '''
        if self._running:
            return

        self._run_thread = RunSimThread(self.run, model)
        self._run_thread.start()
        self._watch_thread = RunSimThread(self.watch, model)
        self._watch_thread.start()

    def join_run_thread(self):
        r'''Wait until the thread finishes
        '''
        if self._run_thread == None:
            self._running = False
            return
        self._run_thread.join()
        self._watch_thread.join()

    def render(self):
        progress_bar_widgets = []
        self.run_button = ipw.Button(#description='Run',
                            icon='fa-play',
                            tooltip='Run with a progress bar',
                            layout=ipw.Layout(width='42px', height='24px'))
        self.run_button.style.button_color = 'gray'

        t_max = getattr(self.model, self.time_max)
        self.pb = ipw.FloatProgress(min=0, max=t_max, layout=ipw.Layout(height='30px'))

        def run_in_thread(change):
            self.run_button.style.button_color = 'lightgray'
            self.reset_button.style.button_color = 'lightgray'
            self.interrupt_button.style.button_color = 'gray'
            t_max = getattr(self.model, self.time_max)
            self.pb.max = t_max
            if self.interrupt_var:
                setattr(self.model, self.interrupt_var, False)
            self.run_thread(self.model)

        self.run_button.on_click(run_in_thread)
        progress_bar_widgets.append(self.run_button)
        progress_bar_widgets.append(self.pb)
        # define the reset action
        if not(self.interrupt_var is None):
            self.interrupt_button = ipw.Button(icon='fa-pause',
                                      tooltip='Interrupt',
                                      layout=ipw.Layout(width='42px', height='24px'))
            self.interrupt_button.style.button_color = 'lightgray'
            def interrupt_button_clicked(change):
                if not self._running:
                    return
                self._running = False
                setattr(self.model, self.interrupt_var, True)
                self.run_button.style.button_color = 'gray'
                self.reset_button.style.button_color = 'gray'
                self.interrupt_button.style.button_color = 'lightgray'
            self.interrupt_button.on_click(interrupt_button_clicked)
            progress_bar_widgets.append(self.interrupt_button)

        if self.reset_method:
            reset_sim = getattr(self.model, self.reset_method)
            self.reset_button = ipw.Button(#description='Reset',
                                      icon='fa-fast-backward',
                                      tooltip='Reset',
                                      layout=ipw.Layout(width='42px', height='24px'))
            self.reset_button.style.button_color = 'lightgray'
            def reset_button_clicked(change):
                if self._running:
                    return
                self.run_button.style.button_color = 'gray'
                self.reset_button.style.button_color = 'lightgray'
                self.interrupt_button.style.button_color = 'lightgray'
                reset_sim()
                self.ui_pane.interactor.update_plot(self.ui_pane.index)
                self.pb.value = 0
            self.reset_button.on_click(reset_button_clicked)
            progress_bar_widgets.append(self.reset_button)

        progress_box = ipw.HBox(progress_bar_widgets,
                                layout=ipw.Layout(padding='0px'))
        progress_box.layout.align_items = 'center'
        return progress_box

