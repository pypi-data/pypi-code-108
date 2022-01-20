import threading
import time

from progress.bar import Bar
from cnvrgv2.utils.converters import convert_bytes


def init_progress_bar_for_cli(name, total_files_size):
    """
    Inits a progress bar for cli purposes. Adds the unit to use and a mutex to the progress bar object
    @param name: Name of the progress bar
    @param total_files_size: total size of files to handle in the progress bar
    @return: The progress bar object
    """
    total_files_size, unit = convert_bytes(total_files_size)
    progress_bar = Bar(name, max=total_files_size, suffix='%(index).2f / %(max).2f ' + unit)
    progress_bar.unit = unit
    progress_bar.mutex = threading.Lock()
    progress_bar.last_next_call = None
    progress_bar.throttled_next_interval = 1  # in seconds
    progress_bar.throttled_next = throttled_next(progress_bar)
    return progress_bar


def throttled_next(self):
    def custom_next(progress):
        current_time = time.time()
        if self.last_next_call is None \
           or current_time > self.last_next_call + self.throttled_next_interval\
           or self.index + progress >= self.max:
            self.next(progress)
            self.last_next_call = current_time
        else:
            self.index = self.index + progress

    return custom_next
