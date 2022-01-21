try:
    pass

    have_colorama = True
except:
    have_colorama = False
import sys

from structlog.dev import ConsoleRenderer
from structlog.stdlib import ProcessorFormatter

from .renderers import ThemeableConsoleRenderer

have_stdout = sys.stdout.isatty()


class ConsoleFormatter(ProcessorFormatter):
    """
    Line logger, intended for ttys.

    This class is a helper to get json dict configurable

    Example:
     "formatters": {
        "axrx_console": {
            "()": "ax.utils.logging.structlog.ConsoleFormatter",
            "colors": true
        },

    """

    def __init__(
        self, colors='auto', theme=None, val_formatters=None, fmt_vals=None, **kw
    ):
        """we use the built in colorama based colorizer only when colors=True
        """
        if colors == 'auto':
            colors = True if have_stdout else False

        if (
            not theme
            and not fmt_vals
            and (not colors or (colors is True and have_colorama))
        ):
            # the sl default:
            r = ConsoleRenderer(colors=colors, **kw)
        else:
            # ours. no colorama dependency, themes, coloring features
            r = ThemeableConsoleRenderer(
                colors=colors,
                theme=theme,
                val_formatters=val_formatters,
                fmt_vals=fmt_vals,
                **kw
            )

        ProcessorFormatter.__init__(
            self,
            processor=r
            # , foreign_pre_chain = pre_chain
            ,
            keep_exc_info=True,
            keep_stack_info=False,  # py3 only
        )
