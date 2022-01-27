import copy
import bokeh
from packaging import version
import inspect
from functools import partial
from enum import Enum
from bokeh.layouts import row, column
import bokeh.models
import numpy as np
import bokeh.plotting
from bokeh.models import WheelPanTool

from tornado import gen


class LogLevel(Enum):
    """ Enum with log levels from logging module"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class LoggerBox:
    """
    Logger with test text box widget to show logs of test apps
    """

    def __init__(self, doc,
                 log_level: int,
                 width: int = 1600,
                 height: int = 300,
                 text_font_size: int = 10,
                 text_font: str = 'monospace',
                 enable_dark_scheme: bool = True,
                 max_history: int = -1,
                 long_class_name: bool = True,
                 ):
        """
        If used in bokeh async function without document lock, extra=dict(async_on=True) needs to be provided as
        kwargs in logging call.

        Examples
        --------
           self.logger.debug("example msg", extra=dict(async_on=True))

        Parameters
        ----------
        doc:
            Bokeh document
        log_level:
            log level int, possible values [0, 10, 20, 30, 40, 50]
        width:
            width of the logger box window
        height:
            height of the logger box window
        text_font_size:
            text font size of the log msg in the logger pox
        text_font:
            type of the text font
        enable_dark_scheme:
            use dark scheme for logger box window
        max_history:
            number of items to keep in history, if -1 or 0 endless history is used
        long_class_name:
            display the full class instance
        """
        self.logger = self

        self.bokeh_document = doc

        self.height = 120
        self.current_y = -self.height

        black = '#201F1D'
        white = '#F0F0F0'
        if enable_dark_scheme:
            figure_color = black
            text_color = white
        else:
            figure_color = white
            text_color = black

        self.height = max(200, height)
        self.width = width
        self.long_class_name = long_class_name

        # empirical tested y range conversion
        coeff = np.array([-1.56666667e+02, 1.77500000e+00, 4.16666667e-05])
        self.y_range_end = (coeff[0] + coeff[1]*self.height + coeff[2]*self.height**2)
        self.y_range_start = -(coeff[0] + coeff[1]*self.height + coeff[2]*self.height**2)

        # text_font_size
        self.text_font_size = f'{int(text_font_size)}pt'
        # self.item_height = min(-2.5 * text_font_size, -10)
        # self.space_between_items = -2
        self.item_height = self.calculate_item_height(text_font_size)
        self.space_between_items = 2
        self.x = 5
        self.max_history = max_history

        self.wheel_pan = WheelPanTool()
        self.wheel_pan.dimension = 'height'

        self.bokeh_figure = bokeh.plotting.figure(width=self.width, plot_height=self.height,
                                                  tools=[self.wheel_pan, 'ypan'], x_axis_location=None, y_axis_location=None,
                                                  toolbar_location=None, )
        self.bokeh_figure.toolbar.active_scroll = self.wheel_pan
        self.bokeh_figure.background_fill_color = figure_color
        self.bokeh_figure.grid.grid_line_color = None
        bounds = (None, None) if version.parse(bokeh.__version__) < version.Version("2.3.0") else None
        self.bokeh_figure.y_range = bokeh.models.Range1d(0, self.y_range_end, bounds=bounds)
        self.x_range = bokeh.models.Range1d(0, width)
        self.bokeh_figure.x_range = self.x_range

        self.ds_text = bokeh.models.ColumnDataSource({'x': [], 'y': [], 'text': []})
        self.label_set = bokeh.models.LabelSet(x='x', x_units='data', y='y', y_units='data', text='text',
                                               source=self.ds_text, text_color=text_color, text_font=text_font)
        self.text_size = f'{int(text_font_size)}pt'
        self.label_set.text_font_size = self.text_size
        self.bokeh_figure.add_layout(self.label_set)

        try:
            self.level = LogLevel(log_level)
        except ValueError as v:
            raise ValueError(f'LoggerBox: invalid log_level {log_level}: {v}')
        level_options = [(str(l.value), l.name) for l in LogLevel]
        self.selector_level = bokeh.models.Select(title="Level", options=level_options, value=str(self.level.value),
                                                  width=120)
        self.selector_level.on_change('value', self.callback_change_level)

        font_sizes = [str(i) for i in range(5, 26)]
        self.selector_fontsize = bokeh.models.Select(title="Fontsize", options=font_sizes, value=str(text_font_size),
                                                     width=120)
        self.selector_fontsize.on_change('value', self.callback_fontsize)

        self.widgets = [self.selector_level, self.selector_fontsize]
        ws = row(*self.widgets, width=75 + 75 + 120 + 20 + 120)
        self.layout = column(ws, row(self.bokeh_figure))

    def get_class_from_frame(self, fr):
        """This function tries to find the name of the class which function send the log msg"""
        args, _, _, value_dict = inspect.getargvalues(fr)
        # we check the first parameter for the frame function is named 'self'
        if len(args) and args[0] == 'self':
            # in that case, 'self' will be referenced in value_dict
            instance = value_dict.get('self', None)
            if instance:
                # return its class
                class_type = getattr(instance, '__class__', None)
                if class_type:
                    if self.long_class_name:
                        return str(class_type)
                    else:
                        return str(class_type.__name__)
        return ''

    def isEnabledFor(self, level):
        """ mimic python logging.logger.isEnabledFor """
        return level <= self.level.value

    @property
    def layout_components(self):
        """This property returns the layout components"""
        return {'widgets': self.widgets, 'figures': [self.bokeh_figure]}

    def callback_fontsize(self, attrn, old, text_font_size) -> None:
        """This function sets a new fontsize"""
        text_font_size = int(text_font_size)
        self.item_height = self.calculate_item_height(text_font_size)
        self.text_size = f'{int(text_font_size)}pt'
        self.label_set.text_font_size = self.text_size
        self.update_data_source()

    def callback_change_level(self, attrn, old, new):
        """This function set the new log level"""
        self.level = LogLevel(int(new))

    @staticmethod
    def calculate_item_height(text_font_size):
        """Calculate the item height"""
        return max(2.5*text_font_size, 10)

    @gen.coroutine
    def update_data_source(self, msg: str = ''):
        """This function calculates and updates the position of all log msg, including the new msg if provided"""
        all_texts = self.ds_text.data['text'].copy()
        if msg:
            all_texts.append(msg)

        if -1 < self.max_history < len(all_texts):
            s_index = len(all_texts) - self.max_history
            all_texts = all_texts[s_index:len(all_texts)]

        x = [self.x]*len(all_texts)
        n = np.arange(0, len(all_texts), 1)[::-1]
        y = (self.item_height + self.space_between_items)*n
        dummy_dict = {'text': all_texts, 'x': x, 'y': y}

        self.ds_text.data = dummy_dict
        self.bokeh_figure.y_range.end = self.y_range_end
        self.bokeh_figure.y_range.start = 0

    @staticmethod
    def _message(level, name, msg, *args, **kwargs):
        """This function formats the log msg with level, class name, msg, and additional args"""
        message = '{}'.format(level)
        if name:
            message += ' - {}'.format(name)
        if msg:
            message += ' - msg: {}'.format(msg)
        if args:
            message += ' - args: {}'.format(', '.join([str(arg) for arg in args]))
        if kwargs:
            message += ' - kwargs: {}'.format(', '.join(['{}={}'.format(str(k), str(v)) for k, v in kwargs.items()]))
        return message

    def display_msg(self, msg_level: str, name, msg, *args, **kwargs):
        """This function calls the update function either for async or sync mode"""
        formatted_msg = self._message(msg_level, name, msg, *args, **kwargs)
        if 'extra' in kwargs and 'async_on' in kwargs['extra'] and kwargs['extra']['async_on']:
            if self.bokeh_document is None:
                return
            self.bokeh_document.add_next_tick_callback(partial(self.update_data_source,
                                                               msg=formatted_msg))
        else:
            self.update_data_source(formatted_msg)

    def debug(self, msg, *args, **kwargs):
        """This function logs debug messages"""
        if self.level.value <= LogLevel.DEBUG.value:
            name = self.get_class_from_frame(inspect.stack()[1][0])
            self.display_msg('DEBUG', name, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """This function logs info messages"""
        if self.level.value <= LogLevel.INFO.value:
            name = self.get_class_from_frame(inspect.stack()[1][0])
            self.display_msg('INFO', name, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """This function logs error messages"""
        if self.level.value <= LogLevel.ERROR.value:
            name = self.get_class_from_frame(inspect.stack()[1][0])
            self.display_msg('ERROR', name, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """This function logs exception messages"""
        if self.level.value <= LogLevel.ERROR.value:
            name = self.get_class_from_frame(inspect.stack()[1][0])
            self.display_msg('EXCEPTION', name, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """This function logs critical messages"""
        if self.level.value <= LogLevel.CRITICAL.value:
            name = self.get_class_from_frame(inspect.stack()[1][0])
            self.display_msg('CRITICAL', name, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """This function logs warning messages"""
        if self.level.value <= LogLevel.WARNING.value:
            name = self.get_class_from_frame(inspect.stack()[1][0])
            self.display_msg('WARNING', name, msg, *args, **kwargs)
