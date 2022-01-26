

from .log import LoggingGuiMixin
from .nodeid import NodeIDGuiMixin
from .busy import BusySpinnerGuiMixin
from .background import OverlayWindowGuiMixin
from .marquee import MarqueeGuiMixin
from .text import AdvancedTextGuiMixin

from .log import NodeLoggingMixin
from .nodeid import NodeIDMixin
from .busy import NodeBusyMixin
from .http import HttpClientMixin
from .shell import BaseShellMixin
from .text import AdvancedTextMixin

from .resources import ResourceManagerMixin


class BaseIoTNode(ResourceManagerMixin, HttpClientMixin, BaseShellMixin,
                  NodeBusyMixin, AdvancedTextMixin, NodeLoggingMixin, NodeIDMixin):
    _has_gui = False

    def __init__(self, *args, **kwargs):
        super(BaseIoTNode, self).__init__(*args, **kwargs)

    def install(self):
        super(BaseIoTNode, self).install()
        self._log.info("Installing Node with ID {log_source.id}")

    def start(self):
        super(BaseIoTNode, self).start()
        self._log.info("Starting Node with ID {log_source.id}")

    def stop(self):
        super(BaseIoTNode, self).stop()
        self._log.info("Stopping Node with ID {log_source.id}")


class BaseIoTNodeGui(NodeIDGuiMixin, BusySpinnerGuiMixin, LoggingGuiMixin,
                     MarqueeGuiMixin, AdvancedTextGuiMixin, OverlayWindowGuiMixin,
                     BaseIoTNode):

    def __init__(self, *args, **kwargs):
        self._application = kwargs.pop('application')
        self._gui_root = None
        super(BaseIoTNodeGui, self).__init__(*args, **kwargs)

    @staticmethod
    def _gui_disable_multitouch_emulation():
        from kivy.config import Config
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

    def gui_setup(self):
        self._gui_disable_multitouch_emulation()
        super(BaseIoTNodeGui, self).gui_setup()
        # # Setup GUI elements from other Mixins
        # OverlayWindowGuiMixin.gui_setup(self)
        # NodeIDGuiMixin.gui_setup(self)
        # LoggingGuiMixin.gui_setup(self)
        return self.gui_root
