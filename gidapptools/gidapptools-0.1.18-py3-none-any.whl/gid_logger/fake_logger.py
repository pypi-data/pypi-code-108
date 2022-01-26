"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import inspect
from typing import Any, Union, Literal, Callable, Optional
from pathlib import Path
from datetime import datetime

# * Third Party Imports --------------------------------------------------------------------------------->
from tzlocal import get_localzone
from rich.box import SQUARE
from rich.text import Text as RichText
from rich.panel import Panel
from rich.style import Style
from rich.console import Console as RichConsole
from rich.console import JustifyMethod
from rich.logging import LogRender
from rich.measure import measure_renderables
from rich.protocol import is_renderable
from rich.containers import Renderables

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

CONSOLE = RichConsole(soft_wrap=True)


def dprint(*args, **kwargs):
    CONSOLE.print(*args, **kwargs)
    CONSOLE.rule()


class FakeLogger:
    styled_log_levels: dict[str, RichText] = {"debug": RichText.styled('DEBUG'.center(8), "logging.level.debug"),
                                              "info": RichText.styled('INFO'.center(8), "logging.level.info"),
                                              "warning": RichText.styled('WARNING'.center(8), "logging.level.warning"),
                                              "error": RichText.styled('ERROR'.center(8), "logging.level.error"),
                                              "critical": RichText.styled('CRITICAL'.center(8), "logging.level.critical")}

    def __init__(self,
                 default_sep: str = " ",
                 default_end: str = "\n",
                 default_style: Optional[Union[str, Style]] = None,
                 default_justify: JustifyMethod = None,
                 as_panel: bool = False,
                 dynamic_panel_title: Union[Literal["output_number", "datetime", "level", "all"], Callable] = "level",
                 ** console_kwargs) -> None:
        self.default_sep = default_sep
        self.default_end = default_end
        self.default_style = default_style
        self.default_justify = default_justify
        _ = console_kwargs.pop("soft_wrap", None)
        self.as_panel = as_panel
        self.dynamic_panel_title = dynamic_panel_title
        self.console = RichConsole(soft_wrap=True, **console_kwargs)
        self.console._log_render = LogRender(show_time=True, show_level=True, omit_repeated_times=False)
        self._output_number = 0
        self._dynamic_panel_title_table = {"output_number": self._get_output_number,
                                           "datetime": self._get_datetime,
                                           "level": self._get_level,
                                           "all": self._get_all,
                                           None: lambda: None}
        self.console.clear()

    def _get_all(self) -> str:
        return '  ' + ' | '.join((self._get_datetime(), self._get_level(extra_back=True), self._get_output_number())) + '  '

    def _get_level(self, extra_back: bool = False) -> str:
        if extra_back is True:
            caller_name = inspect.currentframe().f_back.f_back.f_back.f_code.co_name
        else:
            caller_name = inspect.currentframe().f_back.f_back.f_code.co_name
        return caller_name.upper()

    def _get_datetime(self) -> str:
        date_time = datetime.now(tz=get_localzone())
        return date_time.strftime("%x %X")

    def _get_output_number(self) -> str:
        return str(self._output_number)

    def _get_rule_title(self) -> str:
        if callable(self.dynamic_panel_title):
            return self.dynamic_panel_title()
        return self._dynamic_panel_title_table.get(self.dynamic_panel_title)()

    def debug(self,
              *objects: Any,
              sep: str = ...,
              end: str = ...,
              style: Optional[Union[str, Style]] = ...,
              justify: Optional[JustifyMethod] = ...,
              emoji: Optional[bool] = None,
              markup: Optional[bool] = None,
              highlight: Optional[bool] = None) -> None:
        sep = self.default_sep if sep is ... else sep
        end = self.default_end if end is ... else end
        style = self.default_style if style is ... else style
        justify = self.default_justify if justify is ... else justify
        self._output_number += 1
        objects = tuple(self._fix_obj(o) for o in objects)
        if self.as_panel is True:
            objects = [Panel(Renderables(objects), title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="grey66", color="grey3")), box=SQUARE)]

        self.console.rule(title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="grey66", color="grey3")))
        self.console.print(*objects, sep=sep, end=end, style=style, justify=justify, emoji=emoji, markup=markup, highlight=highlight)

    def info(self,
             *objects: Any,
             sep: str = ...,
             end: str = ...,
             style: Optional[Union[str, Style]] = ...,
             justify: Optional[JustifyMethod] = ...,
             emoji: Optional[bool] = None,
             markup: Optional[bool] = None,
             highlight: Optional[bool] = None) -> None:
        sep = self.default_sep if sep is ... else sep
        end = self.default_end if end is ... else end
        style = self.default_style if style is ... else style
        justify = self.default_justify if justify is ... else justify
        self._output_number += 1
        objects = tuple(self._fix_obj(o) for o in objects)
        if self.as_panel is True:
            objects = [Panel(Renderables(objects), title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="light_sky_blue1", color="dark_green")), box=SQUARE)]

        self.console.rule(title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="light_sky_blue1", color="dark_green")))
        self.console.print(*objects, sep=sep, end=end, style=style, justify=justify, emoji=emoji, markup=markup, highlight=highlight)

    def warning(self,
                *objects: Any,
                sep: str = ...,
                end: str = ...,
                style: Optional[Union[str, Style]] = ...,
                justify: Optional[JustifyMethod] = ...,
                emoji: Optional[bool] = None,
                markup: Optional[bool] = None,
                highlight: Optional[bool] = None) -> None:
        sep = self.default_sep if sep is ... else sep
        end = self.default_end if end is ... else end
        style = self.default_style if style is ... else style
        justify = self.default_justify if justify is ... else justify
        self._output_number += 1
        objects = tuple(self._fix_obj(o) for o in objects)
        if self.as_panel is True:
            objects = [Panel(Renderables(objects), title=RichText.styled(self._get_rule_title(), style=Style(overline=True, underline=True, color="bright_white")), box=SQUARE)]

        self.console.rule(title=RichText.styled(self._get_rule_title(), style=Style(overline=True, underline=True, color="bright_white")))
        self.console.print(*objects, sep=sep, end=end, style=style, justify=justify, emoji=emoji, markup=markup, highlight=highlight)

    def critical(self,
                 *objects: Any,
                 sep: str = ...,
                 end: str = ...,
                 style: Optional[Union[str, Style]] = ...,
                 justify: Optional[JustifyMethod] = ...,
                 emoji: Optional[bool] = None,
                 markup: Optional[bool] = None,
                 highlight: Optional[bool] = None) -> None:
        sep = self.default_sep if sep is ... else sep
        end = self.default_end if end is ... else end
        style = self.default_style if style is ... else style
        justify = self.default_justify if justify is ... else justify
        self._output_number += 1
        objects = tuple(self._fix_obj(o) for o in objects)
        if self.as_panel is True:
            objects = [Panel(Renderables(objects), title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="dark_red", color="white")), box=SQUARE)]

        width = measure_renderables(self.console, options=self.console.options, renderables=objects).maximum
        self.console.line()
        self.console.rule(title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="dark_red", color="white")))
        self.console.print("!" * width)
        self.console.print(*objects, sep=sep, end=end, style=style, justify=justify, emoji=emoji, markup=markup, highlight=highlight)
        self.console.print("!" * width)
        self.console.line()

    def error(self,
              *objects: Any,
              sep: str = ...,
              end: str = ...,
              style: Optional[Union[str, Style]] = ...,
              justify: Optional[JustifyMethod] = ...,
              emoji: Optional[bool] = None,
              markup: Optional[bool] = None,
              highlight: Optional[bool] = None) -> None:
        sep = self.default_sep if sep is ... else sep
        end = self.default_end if end is ... else end
        style = self.default_style if style is ... else style
        justify = self.default_justify if justify is ... else justify
        self._output_number += 1
        objects = tuple(self._fix_obj(o) for o in objects)

        if self.as_panel is True:
            objects = [Panel(Renderables(objects), title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="yellow3", color="red")), box=SQUARE)]

        self.console.rule(title=RichText.styled(self._get_rule_title(), style=Style(bold=True, bgcolor="yellow3", color="red")))
        self.console.print(*objects, sep=sep, end=end, style=style, justify=justify, emoji=emoji, markup=markup, highlight=highlight)

    @staticmethod
    def _fix_obj(in_obj):
        if is_renderable(in_obj):
            return in_obj
        return str(in_obj)


fake_logger = FakeLogger(as_panel=False, dynamic_panel_title="all", default_justify=None)

# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
