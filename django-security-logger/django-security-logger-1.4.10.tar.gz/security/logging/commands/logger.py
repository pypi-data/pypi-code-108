from django.utils.timezone import now

from security.enums import LoggerName
from security.logging.common import SecurityLogger
from security.backends.signals import (
    command_started, command_output_updated, command_finished, command_error,
)


class CommandLogger(SecurityLogger):

    name = LoggerName.COMMAND

    def log_started(self, name, input, is_executed_from_command_line, parent_log=None):
        self.data.update(dict(
            name=name,
            input=input,
            is_executed_from_command_line=is_executed_from_command_line,
            start=now()
        ))
        command_started.send(sender=CommandLogger, logger=self)

    def log_finished(self):
        self.data.update(dict(
            stop=now()
        ))
        command_finished.send(sender=CommandLogger, logger=self)

    def log_output_updated(self, output):
        self.data['output'] = output
        command_output_updated.send(sender=CommandLogger, logger=self)

    def log_exception(self, ex_tb):
        self.data.update(dict(
            error_message=ex_tb,
            stop=now()
        ))
        command_error.send(sender=CommandLogger, logger=self)
