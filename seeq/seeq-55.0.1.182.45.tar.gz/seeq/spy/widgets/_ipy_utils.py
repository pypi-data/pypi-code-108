import logging
from ipywidgets import CoreWidget
from seeq.spy._errors import *


class WidgetLogHandler(logging.Handler):
    """
    A class to allow writing of log values to an output widget.
    """

    def __init__(self):
        super().__init__()
        self.output_widget = None
        self.maximum_lines = 1000
        self._concat_valid = [None, 'append', 'prepend']
        self._concat = False
        self._delimiter = '\n'

    @property
    def concat(self):
        return self._concat

    @concat.setter
    def concat(self, value):
        if value not in self._concat_valid:
            raise SPyRuntimeError(f'Unrecognized concat value {value}. Valid values: {self._concat_valid}')
        self._concat = value

    @property
    def delimiter(self):
        return self._delimiter

    @delimiter.setter
    def delimiter(self, value):
        if value is not None and not isinstance(value, str):
            raise SPyRuntimeError(f'Delimiters must be strings not {type(value)}: {value}')
        self._delimiter = value

    def set_widget(self, output_widget: CoreWidget, concat: str = None, delimiter: str = '\n'):
        """
        Set the output widget for log messages. The widget must have a "value"
        property.

        The output widget will have it's "value" property updated when a new
        log message is available. "concat" controls where the message is
        added in the output_widget's value and "delimiter" determines how
        messages are separated. If concat=None, the widget's value will be
        replaced by the new message.

        Parameters
        ----------
        output_widget : CoreWidget
            The widget to display the log messages. The widget must have a
            settable "value" property.

        concat : {'append', 'prepend'}, optional
            If messages should be prepended or appended to output_widget.value or
            replace output_widget.value. If unspecified, messages will replace
            output_widget.value. Unrecognized values will raise a RuntimeError

        delimiter : str, default '\n'
            The delimiter between log entries if concat != None
        """
        self.concat = concat
        self.delimiter = delimiter
        self.output_widget = output_widget

    def emit(self, record):
        """
        Log the record to the output widget

        Parameters
        ----------
        record : Logging.LogRecord
            The record that will be handed to the handler
        """

        if self.output_widget is None:
            return

        if not self.output_widget.value:
            value = self.format(record)
        else:
            if self._concat == 'append':
                value = self._trim_lines(self.output_widget.value, 'end')
                value = value + self._delimiter + self.format(record)
            elif self._concat == 'prepend':
                value = self._trim_lines(self.output_widget.value, 'start')
                value = self.format(record) + self._delimiter + value
            else:
                value = self.format(record)

        self.output_widget.value = value

    def _trim_lines(self, value, side):
        """
        Trim "value" to be a length of self.maximum_lines-1 when split in self.delimiter
        :param value: str
            The string to trim
        :param side: {'start', 'end'}
            The side to trim from. 'start' removes lines from the front, 'end' removes lines from the back
        :return:
        str : the trimmed string
        """
        lines = value.split(self.delimiter)
        if 0 < self.maximum_lines <= len(lines):
            if side == 'start':
                return self.delimiter.join(lines[len(lines) - self.maximum_lines + 1:])
            elif side == 'end':
                return self.delimiter.join(lines[:self.maximum_lines - 1])
            else:
                raise SPyRuntimeError(f'Unknown trim side for log messages {side}')
        return value
