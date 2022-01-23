'''The main interface for using the `rpa_logger` package.

This module contains the `rpa_logger.logger.Logger` class and default
functions it uses for its callback parameters.
'''

from sys import stdout
from textwrap import indent
from threading import Event, Thread
from typing import Callable, Hashable, Tuple, TextIO

from .task import *
from .utils.terminal import clear_current_row, print_spinner_and_text, COLORS


def get_indicator(status: str, ascii_only: bool = False) -> Tuple[str, str]:
    '''Default value for `indicator_fn` parameter of
    `rpa_logger.logger.Logger`.

    Args:
        status: Status of the task to be logged.
        ascii_only: If true, use ascii only characters.

    Returns:
        Tuple of color and character to use as the status indicator.
    '''
    if status == SUCCESS:
        return ('green', '✓' if not ascii_only else 'Y',)
    if status == IGNORED:
        return ('magenta', '✓' if not ascii_only else 'I',)
    elif status == FAILURE:
        return ('red', '✗' if not ascii_only else 'X',)
    elif status == ERROR:
        return ('yellow', '!',)
    elif status == SKIPPED:
        return ('blue', '–',)
    elif status == STARTED:
        return ('white', '#',)
    else:
        return ('grey', '?',)


def multiple_active_text(num_active: int) -> str:
    '''Default value for `multiple_fn` parameter of `rpa_logger.logger.Logger`.

    Args:
        num_active: Number of currently active tasks.

    Returns:
        String to print when multiple tasks are in progress.
    '''
    return f'{num_active} tasks in progress'


def is_status_ok(status: str) -> bool:
    '''Default value for `status_ok_fn` parameter of
    `rpa_logger.logger.Logger`.

    Args:
        status: Status to determine OK status for.

    Returns:
        True if given status is OK, False otherwise.
    '''
    return status not in (FAILURE, ERROR,)


class Logger:
    '''Interface for logging RPA tasks.

    Args:
        animations: If true, progress indicator is displayed.
        colors: If true, ANSI escape codes are used when logging to console.
        ascii_only: If true, use ascii only spinner and status indicators.
        target: File to print output to. Defaults to stdout.
        multiple_fn: Function used to determine progress message when multiple
            tasks are in progress. Defaults to
            `rpa_logger.logger.multiple_active_text`.
        indicator_fn: Function used to determine the color and character for
            the status indicator. Defaults to
            `rpa_logger.logger.get_indicator`.
        status_ok_fn: Function used to determine if given task status is ok.
            Defaults to `rpa_logger.logger.get_indicator`.
    '''

    def __init__(
            self,
            animations: bool = True,
            colors: bool = True,
            ascii_only: bool = False,
            print_output_immediately: bool = False,
            target: TextIO = None,
            multiple_fn: Callable[[int], str] = None,
            indicator_fn: Callable[[str, bool], Tuple[str, str]] = None,
            status_ok_fn: Callable[[str], bool] = None):
        self._animations = animations
        self._colors = colors
        self._ascii_only = ascii_only
        self._print_output_immediately = print_output_immediately
        self._target = target or stdout

        self._get_multiple_active_str = multiple_fn or multiple_active_text
        self._get_progress_indicator = indicator_fn or get_indicator
        self._is_status_ok = status_ok_fn or is_status_ok

        self._spinner_thread = None
        self._spinner_stop_event = Event()

        self.suite = TaskSuite(None)
        '''`rpa_logger.task.TaskSuite` where logger stores task data.'''

    def bold(self, text: str) -> str:
        '''Bold given text with ANSI escape codes.

        Args:
            text: Text to be formatted.

        Returns:
            String with formatted text.
        '''
        if not self._colors:
            return text
        return f'\033[1m{text}\033[22m'

    def color(self, text: str, color: str) -> str:
        '''Color given text with ANSI escape codes.

        Args:
            text: Text to be formatted.
            color: Color to format text with. See
                `rpa_logger.utils.terminal.COLORS` for available values.

        Returns:
            String with formatted text.
        '''
        if not self._colors or color not in COLORS:
            return text
        return f'\033[{COLORS[color]}m{text}\033[39m'

    def _print(self, *args, **kwargs):
        return print(*args, file=self._target, **kwargs)

    def error(self, text: str) -> None:
        '''Print error message.

        Args:
            text: Error message text.
        '''
        error_text = self.bold(self.color('ERROR:', 'red'))
        self._print(f'{error_text} {text}')

    def title(self, title: str = None, description: str = None) -> None:
        '''Print title and description of the RPA process.

        Args:
            title: Title to print in bold.
            description: Description to print under the title.
        '''
        self.suite.name = title
        self.suite.description = description

        title_text = f'{self.bold(title)}\n' if title else ''
        self._print(f'{title_text}{description or ""}\n')

    def _print_active(self):
        if not self._animations:
            return

        num_active = len(self.suite.active_tasks)
        if not num_active:
            return
        elif num_active > 1:
            text = self._get_multiple_active_str(num_active)
        else:
            text = self.suite.active_tasks[0].name

        clear_current_row(self._target)
        self.stop_progress_animation()

        self._spinner_thread = Thread(
            target=print_spinner_and_text,
            args=[
                text,
                self._spinner_stop_event,
                self._target,
                self._ascii_only])
        self._spinner_stop_event.clear()
        self._spinner_thread.start()

    def _get_indicator_text(self, status):
        color, symbol = self._get_progress_indicator(status, self._ascii_only)
        return self.bold(self.color(symbol, color))

    def _print_task(self, key):
        task = self.suite.get_task(key)
        indicator_text = self._get_indicator_text(task.status)
        indented_text = indent(task.name, '  ').strip()

        self._print(f'{indicator_text} {indented_text}\n')

    def start_task(self, text: str, key: Hashable = None) -> Hashable:
        '''Create a new active task and print progress indicator.

        Args:
            text: Name or description of the task.
            key: Key to identify the task with. If not provided, new uuid4
                will be used.

        Return:
            Key to control to the created task with.
        '''
        key = self.suite.create_task(text, key)

        if self._print_output_immediately:
            self._print_task(key)

        self._print_active()
        return key

    def stop_progress_animation(self) -> None:
        '''Stop possible active progress indicators.
        Should be used, for example, if the application is interrupted while
        there are active progress indicators.
        '''
        self._spinner_stop_event.set()
        if self._spinner_thread:
            self._spinner_thread.join()
            self._spinner_thread = None

    def finish_task(
            self,
            status: str,
            text: str = None,
            key: Hashable = None) -> None:
        '''Finish active or new task and print its status.

        Calling this method is required to stop the progress spinner of a
        previously started task.

        Args:
            status: Status string used to determine the status indicator.
            text: Text to describe the task with. Defaults to the text used
                when the task was created if `key` is given.
            key: Key of the previously created task to be finished.
        '''
        self.stop_progress_animation()

        if not key:
            if not text:
                raise RuntimeError(
                    f'No text provided or found for given key ({key}).')
            return self.log_task(status, text)

        self.suite.finish_task(key, status)

        task = self.suite.get_task(key)
        if text:
            task.name = text

        if self._print_output_immediately and task.output:
            clear_current_row(self._target)
            self._print('')

        self._print_task(key)

        if not self._print_output_immediately:
            output_text = indent(
                '\n'.join(i.text for i in task.output), '  ').rstrip()
            if output_text:
                self._print(f'{output_text}\n')

        self._print_active()

    def log_task(self, status: str, text: str) -> None:
        '''Create and finish a new task.

        This method can be used when the task to be logged was not previously
        started.

        Args:
            status: Status to use for the finished task.
            text: Name of the task.
        '''
        key = self.suite.log_task(status, text)
        self._print_task(key)
        self._print_active()
        return key

    def log_metadata(
            self,
            key: str,
            value: Any,
            task_key: Hashable = None) -> None:
        '''Log metadata into the loggers task suite or any of its tasks.

        Args:
            key: Key for the metadata item.
            value: Value for the metadata item. If task data is saved as json
                or yaml, this value must be serializable.
            task_key: Key of a task to log metadata into. If None, metadata
                is logged to the suite.
        '''
        return self.suite.log_metadata(key, value, task_key)

    def log_output(self, key: Hashable, text: str,
                   stream: str = 'stdout') -> None:
        '''Append new `rpa_logger.utils.output.OutputText` to task output.

        Args:
            key: Key of the task to log output to.
            text: Output text content.
            stream: Output stream. Defaults to `stdout`.
        '''
        if self._print_output_immediately:
            self.stop_progress_animation()
            self._print(indent(text, '  '))
            self._print_active()

        self.suite.log_output(key, text, stream)

    def _num_failed_tasks(self) -> int:
        summary = self.suite.task_status_counter
        return sum(summary.get(status, 0)
                   for status in summary if not self._is_status_ok(status))

    def finish_suite(self, success_status: str = SUCCESS,
                     failure_status: str = ERROR) -> None:
        '''Finish loggers task suite.

        Args:
            success_status: Status to use as suite status if all tasks have
                ok status.
            failure_status: Status to use as suite status if some of the tasks
                have non-ok status.
        '''
        if self._num_failed_tasks() > 0:
            return self.suite.finish(failure_status)

        return self.suite.finish(success_status)

    def summary(self) -> int:
        '''Print summary of the logged tasks.

        Returns:
            Number of failed (status is either `FAILURE` or `ERROR`) tasks.
        '''
        summary = self.suite.task_status_counter

        text = self.bold('Summary:')
        for status in summary:
            indicator = self._get_indicator_text(status)
            text += f'\n{indicator} {status.title()}: {summary.get(status)}'

        self._print(text)

        return self._num_failed_tasks()
