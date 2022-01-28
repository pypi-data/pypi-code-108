import textwrap

from ..procedures.procedure import Procedure
from ..units.messenger import Messenger


class RunFunction(Procedure):
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self, messenger: Messenger):
        args = textwrap.shorten(repr(self.args), width=100, placeholder="...")
        kwargs = textwrap.shorten(repr(self.kwargs), width=100, placeholder="...")
        messenger.info(f"Run function `{self.function.__name__}` "
                       f"with args: `{args}` "
                       f"and kwargs: `{kwargs}`")

        if hasattr(self.function, "__globals__"):
            self.function.__globals__["print"] = messenger.print  # inject messenger.print as print
        return self.function(*self.args, **self.kwargs)
