from contextlib import contextmanager
try:
    from accpac import UI
except ImportError:
    UI = object
    pass

@contextmanager
def bareui(close=True):
    """Get a BareUI instance temporarily.

    Useful for running scripts that pop up messages but don't need to
    leave the UI window lingering.

    :param close: whether to automatically close the UI. Disable to capture
                  lingering errors.
    :type close: bool

    .. code-block:: python

        # myextenderscript.py
        from accpac import *
        from extools.exui.bare import bareui

        def main(*args, **kwargs):
            with bareui():
                showMessageBox("This will be displayed!")
                # ...
    """
    bui = BareUI()
    try:
        yield bui
    finally:
        if close:
            bui.closeUI()

class BareUI(UI):
    """Am empty UI for running scripts without displayinga window."""

    def __init__(self):
        super().__init__()
        self.show()
