import sys

import traceback

from security.config import settings
from security.enums import LoggerName
from security.logging.common import get_last_logger


def get_command_stream():
    last_command_logger = get_last_logger(LoggerName.COMMAND)
    return last_command_logger.stream if last_command_logger is not None else sys.stdout


class CommandExecutor:
    """
    A helper class that runs a django command and logs details about its run into DB.
    """

    def __init__(self, command_function, command_args=None, command_kwargs=None, stdout=None, stderr=None, **kwargs):
        """
        Initializes the command logger.

        Arguments:
            command_function: Callable that implements the command.
            stdout: Custom stream where command's standard output will be written.
            stderr: Custom stream where command's error output will be written.
            **kwargs: Keyword arguments passed to CommandLog model.
        """
        assert 'name' in kwargs, 'Key name must be provided in kwargs'

        self.command_function = command_function
        self.command_args = command_args or ()
        self.command_kwargs = command_kwargs or {}

        self.kwargs = kwargs
        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr

    def run(self):
        """
        Runs the command function and returns its return value or re-raises any exceptions. The run of the command will
        not be logged if it is in excluded commands setting.
        """
        from security.logging.commands.logger import CommandLogger
        from security.utils import LogStringIO, TeeStringIO

        if self.kwargs['name'] in settings.COMMAND_LOG_EXCLUDED_COMMANDS:
            return self.command_function(
                stdout=self.stdout, stderr=self.stderr, *self.command_args, **self.command_kwargs
            )

        with CommandLogger() as command_logger:
            command_logger.log_started(**self.kwargs)
            self.output = LogStringIO(
                flush_callback=lambda output_stream: command_logger.log_output_updated(output_stream.getvalue())
            )
            command_logger.stream = self.output
            stdout = TeeStringIO(self.stdout, self.output)
            stderr = TeeStringIO(self.stderr, self.output)
            try:
                ret_val = self.command_function(
                    stdout=stdout, stderr=stderr, *self.command_args, **self.command_kwargs
                )
                command_logger.log_finished()
                return ret_val
            except (Exception, KeyboardInterrupt, SystemExit) as ex:  # pylint: disable=W0703
                command_logger.log_exception(traceback.format_exc())
                raise ex
            finally:
                self.output.close()
