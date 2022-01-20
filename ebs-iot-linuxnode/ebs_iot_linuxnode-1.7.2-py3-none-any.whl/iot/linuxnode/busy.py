

from kivy.garden.progressspinner import TextureProgressSpinner
from .widgets.colors import Gradient
from .basemixin import BaseMixin
from .basemixin import BaseGuiMixin
from .log import NodeLoggingMixin


class NodeBusyMixin(NodeLoggingMixin, BaseMixin):
    def __init__(self, *args, **kwargs):
        super(NodeBusyMixin, self).__init__(*args, **kwargs)
        self._busy = False

    @property
    def busy(self):
        if self._busy > 0:
            return True
        else:
            return False

    def busy_set(self):
        self._busy += 1

    def busy_clear(self):
        self._busy -= 1
        if self._busy < 0:
            self.log.warn("Busy cleared too many times!")
            self._busy = 0

    def _busy_setter(self, value):
        self.log.debug("Setting node busy status to {0}".format(value))
        self._busy = value


class BusySpinnerGuiMixin(NodeBusyMixin, BaseGuiMixin):
    _gui_busy_spinner_class = TextureProgressSpinner
    _gui_busy_spinner_props = {}

    def __init__(self, *args, **kwargs):
        self._gui_busy_spinner = None
        super(BusySpinnerGuiMixin, self).__init__(*args, **kwargs)

    def busy_set(self):
        super(BusySpinnerGuiMixin, self).busy_set()
        self._gui_update_busy()

    def busy_clear(self):
        super(BusySpinnerGuiMixin, self).busy_clear()
        self._gui_update_busy()

    def _gui_update_busy(self):
        if self.busy is True:
            self._gui_busy_show()
        else:
            self._gui_busy_clear()

    def _gui_busy_show(self):
        parent = self.gui_busy_spinner.parent
        if not parent:
            self.gui_notification_row.add_widget(self.gui_busy_spinner)
            self.gui_notification_update()

    def _gui_busy_clear(self):
        parent = self.gui_busy_spinner.parent
        if parent:
            parent.remove_widget(self.gui_busy_spinner)
            self.gui_notification_update()

    @property
    def gui_busy_spinner(self):
        if not self._gui_busy_spinner:
            props = self._gui_busy_spinner_props
            _texture = Gradient.horizontal(self.gui_color_1, self.gui_color_2)
            props['texture'] = _texture
            self._gui_busy_spinner = self._gui_busy_spinner_class(
                size_hint=(None, None), height=50, pos_hint={'left': 1},
                **props
            )
        return self._gui_busy_spinner
