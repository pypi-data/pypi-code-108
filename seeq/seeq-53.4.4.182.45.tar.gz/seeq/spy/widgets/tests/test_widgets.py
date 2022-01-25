import logging

import ipywidgets as ipw
import pytest

from seeq import spy


@pytest.mark.unit
def test_log_handler_trim_lines():
    widget_log_handler = spy.widgets.WidgetLogHandler()
    widget_log_handler.delimiter = '\n'
    widget_log_handler.maximum_lines = 3
    test_string = 'Line 1\nLine 2\nLine 3\nLine 4'
    trim_start = widget_log_handler._trim_lines(test_string, 'start')
    assert trim_start.split(widget_log_handler.delimiter) == test_string.split(widget_log_handler.delimiter)[2:]

    trim_end = widget_log_handler._trim_lines(test_string, 'end')
    assert trim_end.split(widget_log_handler.delimiter) == test_string.split(widget_log_handler.delimiter)[:-2]


@pytest.mark.unit
def test_log_handler():
    log_output_widget = ipw.Textarea(
        value='Line 1\nLine 2\nLine 3'
    )
    widget_log_handler = spy.widgets.WidgetLogHandler()
    # a fake log record
    test_message = 'Test Message'
    test_record = logging.LogRecord(name='test_logger',
                                    level=logging.DEBUG,
                                    pathname='test_file_path',
                                    lineno=100,
                                    msg=test_message,
                                    args=[],
                                    exc_info=None)
    widget_log_handler.set_widget(log_output_widget, concat='append', delimiter='\n')
    widget_log_handler.emit(test_record)
    assert log_output_widget.value.split('\n')[-1] == test_message

    widget_log_handler.concat = 'prepend'
    widget_log_handler.emit(test_record)
    assert log_output_widget.value.split('\n')[0] == test_message

    assert len(log_output_widget.value.split('\n')) == 5
