

import os

from ..log import NodeLoggingMixin
from ..http import HttpClientMixin
from ..basemixin import BaseGuiMixin

from ..widgets.image import BleedImage
from ..widgets.labels import ColorLabel

from ..widgets.image import StandardImage
from ..widgets.labels import SelfScalingLabel
from ..widgets.colors import ColorBoxLayout


class ModularApiEngineManagerMixin(HttpClientMixin, NodeLoggingMixin):
    def __init__(self, *args, **kwargs):
        super(ModularApiEngineManagerMixin, self).__init__(*args, **kwargs)
        self._api_engines = []
        self._api_primary = None

    def modapi_install(self, engine, primary=False):
        self.log.info("Installing Modular API Engine {0}".format(engine))
        self._api_engines.append(engine)
        if primary:
            self._api_primary = engine

    def modapi_activate(self):
        for engine in self._api_engines:
            self.log.info("Starting Modular API Engine {0}".format(engine))
            engine.start()

    def modapi_engine(self, name):
        for engine in self._api_engines:
            if engine.name == name:
                return engine

    def modapi_stop(self):
        for engine in self._api_engines:
            self.log.info("Stopping Modular API Engine {0}".format(engine))
            engine.stop()

    def start(self):
        super(ModularApiEngineManagerMixin, self).start()
        self.modapi_activate()

    def stop(self):
        self.modapi_stop()
        super(ModularApiEngineManagerMixin, self).stop()


class ModularApiEngineManagerGuiMixin(ModularApiEngineManagerMixin, BaseGuiMixin):
    def __init__(self, *args, **kwargs):
        super(ModularApiEngineManagerGuiMixin, self).__init__(*args, **kwargs)

        self._api_internet_link = None
        self._api_internet_link_indicator = None

        self._api_internet_connected = False
        self._api_internet_indicator = None

        self._api_connection_status = {}
        self._api_connection_indicators = {}

    @property
    def modapi_internet_link_indicator(self):
        if not self._api_internet_link_indicator:
            params = {'bgcolor': (0xff / 255., 0x00 / 255., 0x00 / 255., 0.3),
                      'color': [1, 1, 1, 1]}
            self._api_internet_link_indicator = ColorLabel(
                text=self._api_internet_link, size_hint=(None, None),
                height=50, font_size='14sp',
                valign='middle', halign='center', **params
            )

            def _set_label_width(_, texture_size):
                self._api_internet_link_indicator.width = texture_size[0] + 20

            self._api_internet_link_indicator.bind(texture_size=_set_label_width)
        return self._api_internet_link_indicator

    def _modapi_internet_link_indicator_show(self, duration=5):
        _ = self.modapi_internet_link_indicator
        if not self._api_internet_link_indicator.parent:
            self.gui_notification_stack.add_widget(self._api_internet_link_indicator)
            self.gui_notification_update()
        if duration:
            self.reactor.callLater(duration, self._modapi_internet_link_indicator_clear)

    def _modapi_internet_link_indicator_clear(self):
        if self._api_internet_link_indicator and self._api_internet_link_indicator.parent:
            self.gui_notification_stack.remove_widget(self._api_internet_link_indicator)
            self.gui_notification_update()
        self._api_internet_link_indicator = None

    @property
    def modapi_internet_indicator(self):
        if not self._api_internet_indicator:
            _root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            _source = os.path.join(_root, 'images', 'no-internet.png')
            self._api_internet_indicator = BleedImage(
                source=_source, pos_hint={'left': 1},
                size_hint=(None, None), height=50, width=50,
                bgcolor=(0xff / 255., 0x00 / 255., 0x00 / 255., 0.3),
            )
        return self._api_internet_indicator

    def _modapi_internet_indicator_show(self):
        if not self.modapi_internet_indicator.parent:
            self.gui_notification_row.add_widget(self.modapi_internet_indicator)
            self.gui_notification_update()

    def _modapi_internet_indicator_clear(self):
        if self.modapi_internet_indicator.parent:
            self.modapi_internet_indicator.parent.remove_widget(self.modapi_internet_indicator)
            self.gui_notification_update()

    def modapi_connection_indicator(self, prefix):
        if prefix not in self._api_connection_indicators.keys():
            _root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            source = os.path.join(_root, 'images', 'no-server.png')
            indicator = ColorBoxLayout(
                pos_hint={'left': 1}, orientation='vertical', padding=(0, 0, 0, 5),
                size_hint=(None, None), height=70, width=50, spacing=0,
                bgcolor=(0xff / 255., 0x00 / 255., 0x00 / 255., 0.3),
            )
            indicator.add_widget(
                StandardImage(source=source, size_hint=(1, None), height=50)
            )
            indicator.add_widget(
                SelfScalingLabel(text=prefix,
                                 size_hint=(1, None), height=15)
            )

            self._api_connection_indicators[prefix] = indicator
        return self._api_connection_indicators[prefix]

    def _modapi_connection_indicator_show(self, prefix):
        if not self.modapi_connection_indicator(prefix).parent:
            self.gui_notification_row.add_widget(self.modapi_connection_indicator(prefix))
            self.gui_notification_update()

    def _modapi_connection_indicator_clear(self, prefix):
        if self.modapi_connection_indicator(prefix).parent:
            self.modapi_connection_indicator(prefix).parent.remove_widget(self.modapi_connection_indicator(prefix))
            self.gui_notification_update()

    def modapi_signal_internet_link(self, value, prefix):
        self._api_internet_link = value
        self._modapi_internet_link_indicator_show()

    def modapi_signal_internet_connected(self, value, prefix):
        if not value:
            self._modapi_internet_indicator_show()
        else:
            self._modapi_internet_indicator_clear()
        self._api_internet_connected = value

    def modapi_signal_api_connected(self, value, prefix):
        if not value:
            self._modapi_connection_indicator_show(prefix)
        else:
            self._modapi_connection_indicator_clear(prefix)
        self._api_connection_status[prefix] = value
