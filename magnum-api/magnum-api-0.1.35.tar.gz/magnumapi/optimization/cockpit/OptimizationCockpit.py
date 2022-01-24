from threading import Timer

import pandas as pd
from IPython.display import display

from magnumapi.optimization.GeneticOptimization import GeneticOptimizationBuilder
from magnumapi.optimization.logger.Logger import Logger
from magnumapi.optimization.cockpit.OptimizationCockpitWidget import OptimizationCockpitWidget
from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig


class RepeatedTimer(object):
    """ Class providing a repeated timer functionality used for updating the optimization cockpit

    """
    def __init__(self, interval: float, function) -> None:
        """ Constructor of a RepeatedTimer instance

        :param interval: interval of function execution (in seconds)
        :param function: function to be executed at regular intervals
        """
        self._timer = None
        self.interval = interval
        self.function = function
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class OptimizationCockpit:
    """ Class displaying and refreshing the optimization cockpit.

    """

    def __init__(self,
                 config: OptimizationConfig,
                 output_subdirectory_dir: str,
                 is_log_y=False) -> None:
        """ Constructor of the OptimizationCockpit class

        :param logger_abs_path: an absolute path to the logger
        :param config: optimization config instance
        :param design_variables_df: a dataframe with optimization objectives
        :param is_log_y: if True, than the score plot has logarithmic y-scale
        """
        self.gen_opt = GeneticOptimizationBuilder.build(config, output_subdirectory_dir)
        self.logger_abs_path = self.gen_opt.logger.logger_abs_path
        self.logger_df = pd.read_csv(self.logger_abs_path, index_col=0)
        self.config = config
        self.is_log_y = is_log_y
        self.widget = None

    def display(self, t_sleep_in_sec=5.0) -> None:
        """ Method displaying the cockpit and starting a timer to refresh the cockpit with a given period.

        :param t_sleep_in_sec: the refresh interval for the cockpit
        """
        if len(self.logger_df):
            self.widget = OptimizationCockpitWidget(self.gen_opt,
                                                    self.logger_df,
                                                    self.config,
                                                    self.is_log_y)
            self.widget.build()
            display(self.widget.show())

            RepeatedTimer(t_sleep_in_sec, self.update_cockpit)
        else:
            raise Warning('The logger dataframe is empty, no data to display!')

    def update_cockpit(self) -> None:
        """ Method updating the cockpit by checking whether an update is available, i.e., the logger was populated with
        new information.

        """
        logger_new_df = pd.read_csv(self.logger_abs_path, index_col=0)
        if len(logger_new_df) > len(self.logger_df):
            self.logger_df = logger_new_df
            self.widget.min_logger_df = Logger.extract_min_rows_from_logger_df(self.logger_df, self.config.n_pop)
            self.widget.widget.data = []
            self.widget.build()
