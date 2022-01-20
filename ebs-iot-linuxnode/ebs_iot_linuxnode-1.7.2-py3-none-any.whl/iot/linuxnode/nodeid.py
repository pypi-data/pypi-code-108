

import netifaces
import uuid

from twisted.internet import task

from .widgets.labels import ColorLabel
from .widgets.colors import color_set_alpha

from .basemixin import BaseMixin
from .basemixin import BaseGuiMixin

from .config import ConfigMixin


class NodeIDMixin(ConfigMixin, BaseMixin):
    _node_id_netifaces_fallback_interfaces = ['wlp1s0', 'wlan0', 'eth0']

    def __init__(self, *args, **kwargs):
        super(NodeIDMixin, self).__init__(*args, **kwargs)
        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = self._get_id()
        return self._id

    def _get_id(self):
        if self.config.node_id_override is not None:
            return self.config.node_id_override
        getter = "_get_node_id_{0}".format(self.config.node_id_getter)
        params = {'interface': self.config.node_id_interface}
        return getattr(self, getter)(**params).upper()

    def _get_node_id_uuid(self, **_):
        node_id = uuid.getnode()
        if (node_id >> 40) % 2:
            raise OSError("The system does not seem to have a valid MAC")
        return hex(node_id)[2:]

    def _get_node_id_netifaces_guess(self):
        fallback_interfaces = self._node_id_netifaces_fallback_interfaces
        available_interfaces = netifaces.interfaces()
        default_gateway = netifaces.gateways()['default']
        if default_gateway:
            return default_gateway[netifaces.AF_INET][1]
        for iface in fallback_interfaces:
            if iface in available_interfaces:
                return iface

    def _get_node_id_netifaces(self, **kwargs):
        interface = kwargs.get('interface', None)
        if interface is None:
            interface = self._get_node_id_netifaces_guess()
        mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
        return mac.replace(':', '')


class NodeIDGuiMixin(NodeIDMixin, BaseGuiMixin):
    _gui_nodeid_bgcolor = None
    _gui_nodeid_color = None

    def __init__(self, *args, **kwargs):
        super(NodeIDGuiMixin, self).__init__(*args, **kwargs)
        self._gui_id_tag = None
        self._gui_id_task = None

    @property
    def gui_id_tag(self):
        if not self._gui_id_tag:
            params = {'bgcolor': (self._gui_nodeid_bgcolor or
                                  color_set_alpha(self.gui_color_1, 0.4)),
                      'color': [1, 1, 1, 1]}
            self._gui_id_tag = ColorLabel(
                text=self.id, size_hint=(None, None),
                width=250, height=50, font_size='18sp',
                valign='middle', halign='center', **params
            )
        return self._gui_id_tag

    def gui_id_show(self, duration=None):
        if not self.gui_id_tag.parent:
            self.gui_status_stack.add_widget(self.gui_id_tag)
        if duration:
            self.reactor.callLater(duration, self.gui_id_hide)

    def gui_id_hide(self):
        if self.gui_id_tag.parent:
            self.gui_status_stack.remove_widget(self.gui_id_tag)

    def gui_setup(self):
        super(NodeIDGuiMixin, self).gui_setup()
        if not self.config.node_id_display:
            return
        if self.config.node_id_display_frequency:
            self._gui_id_task = task.LoopingCall(
                self.gui_id_show,
                duration=self.config.node_id_display_duration
            )
            self._gui_id_task.start(self.config.node_id_display_frequency)
        else:
            self.gui_id_show(duration=self.config.node_id_display_duration)
