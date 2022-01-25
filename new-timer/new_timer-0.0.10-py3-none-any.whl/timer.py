import time
import math
import logging
import numpy as np
from datetime import datetime

"""
If you want to normaly display message, you need to set log format of logging. Follow the example below:
    # Set logging config.
    FORMAT = '[%(levelname)s] %(message)s'
    DATE_FORMAT = '%Y%m%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)
"""

class ManualTimer(object):
    """
    This class is manual timer.

    Attributes:
    ------
    max: Save maximum elpased time value.

    min: Save minimum elpased time value.

    mean: Save mean elpased time value.


    ## Example:
        from timer import ManualTimer

        timer1 = ManualTimer(name="Print 0 ~ 9999", decimal=2)

        for i in range(10):
            timer1.start()
            for i in range(99999):
                print(i)
            timer1.stop()
    """

    def __init__(self, name="Program", decimal=12, show=True, show_others=False):
        """
        Args:
        -----
        name: Define your timer name.

        decimal: Display to a certain number of decimal places

        show: Show the elapsed time.
        """

        self.name = name
        self.__start_time = float()
        self.__end_time = float()
        self.__elapsed_time = float()

        self.__decimal = decimal
        self.__show = show
        self.__show_others = show_others

        self.max = None
        self.min = None
        self.mean = None
        self.__time_records = np.array([])
    
    def start_time(self)-> float:
        return self.__start_time

    def end_time(self)-> float:
        return self.__end_time

    def elapsed_time(self)-> float:
        return self.__elapsed_time

    def set_name(self, name):
        """
        Set timer name.
        """
        self.name = name
    
    
    def start(self):
        """
        Start the timer.
        """
        self.__start_time = time.time()


    def stop(self):
        """
        Stop the timer.

        returns:
        --------
        hours: elapsed hours.

        minutes: elapsed minutes.

        seconds: elapsed seconds.
        """
        
        self.__end_time = time.time()
        self.__elapsed_time = time.time() - self.__start_time

        # Get each time elapsed.
        self.__time_records = np.append(self.__time_records, self.__elapsed_time)
        logging.debug("self.__time_records: {}".format(self.__time_records))

        hours, minutes, seconds = self.__calc_time(self.__elapsed_time)
        self.__calc_3_values()
        
        if self.__show == True:
            logging.info("{} cost time {} hours {} mins {} secs.".format(self.name, 
                                                                         hours, 
                                                                         minutes,
                                                                         np.round(seconds, self.__decimal)))
        if self.__show_others == True:
            logging.info("{} cost time max({} times): {} hours {} mins {} secs.".format(self.name, 
                                                                                        len(self.__time_records),
                                                                                        self.max[0], 
                                                                                        self.max[1],
                                                                                        np.round(self.max[2], self.__decimal)))
            logging.info("{} cost time min({} times): {} hours {} mins {} secs.".format(self.name, 
                                                                                        len(self.__time_records),
                                                                                        self.min[0], 
                                                                                        self.min[1],
                                                                                        np.round(self.min[2], self.__decimal)))
            logging.info("{} cost time mean({} times): {} hours {} mins {} secs.".format(self.name, 
                                                                                         len(self.__time_records),
                                                                                         self.mean[0], 
                                                                                         self.mean[1],
                                                                                         np.round(self.mean[2], self.__decimal)))
        
        return (hours, minutes, seconds)


    def __calc_time(self, seconds):
        """
        Transfer unit from seconds to hours、minutes and seconds.

        Args:
        -----
        seconds: Input elpased seconds time.
        """
        hours = 0
        minutes = 0

        if seconds < 60:
            pass
        elif seconds/60 >= 1 and seconds/3600 < 1:
            minutes = math.floor(seconds/60 )
            seconds = seconds - minutes*60
        else:
            hours = math.floor(seconds/3600)
            minutes = math.floor((seconds - hours*3600) / 60)
            seconds = seconds - hours*3600 - minutes*60

        return (hours, minutes, seconds)
        
    
    def __calc_3_values(self):
        """
        Calculate maximum、minimum and mean of multiple time records, and transfer unit from seconds to hours、minutes and seconds.
        """

        self.max = self.__calc_time(self.__time_records.max())
        self.min = self.__calc_time(self.__time_records.min())
        self.mean = self.__calc_time(self.__time_records.mean())


class AutoTimer(object):
    """
    This class is automatic timer.

    ## Example:
        from timer import AutoTimer

        a = 0
        with AutoTimer("Pring 0 ~ 9999999", decimal=2):
            for i in range(9999999):
                a += i
                print(a)
    """

    def __init__(self, name="Program", decimal=12, show=True):
        """
        Args:
        -----
        name: Define your timer name.

        decimal: Display to a certain number of decimal places

        show: Show the elapsed time.
        """

        self.name = name
        self.__decimal = decimal
        self.__show = show
        self.__hours = 0
        self.__minutes = 0
        self.__seconds = 0.0

    def __enter__(self):
        """
        Start the timer.
        """
        self.__start = time.time()

    def __exit__(self, *args):
        """
        Stop the timer.

        return:
        -------
        hours: elapsed hours.

        minutes: elapsed minutes.

        seconds: elapsed seconds.
        """

        self.__seconds = time.time() - self.__start
        
        if self.__seconds < 60:
            pass
        elif self.__seconds/60 >= 1 and self.__seconds/3600 < 1:
            self.__minutes = math.floor(self.__seconds/60 )
            self.__seconds = self.__seconds - self.__minutes*60
        elif self.__seconds/3600 >= 1 :
            self.__hours = math.floor(self.__seconds/3600)
            self.__minutes = math.floor((self.__seconds - self.__hours*3600) / 60)
            self.__seconds = self.__seconds - self.__hours*3600 - self.__minutes*60

        if self.__show == True:
            logging.info("{} cost time {} hours {} mins {} secs.".format(self.name, 
                                                                         self.__hours, 
                                                                         self.__minutes,
                                                                         np.round(self.__seconds, self.__decimal)))


def get_now_time(format="%Y-%m-%d %H:%M:%S", show=False):
    """
    Gets current time.
    """
    now = datetime.now()
    now = now.strftime(format)
    
    if show == True:
        logging.info("Current time: {}".format(now))
    
    return now