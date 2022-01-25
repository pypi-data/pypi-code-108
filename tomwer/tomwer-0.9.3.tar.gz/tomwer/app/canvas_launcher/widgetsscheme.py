from orangewidget.workflow.widgetsscheme import (
    WidgetsSignalManager as _WidgetsSignalManager,
    WidgetsScheme as _WidgetsScheme,
    WidgetManager,
)
from orangecanvas.scheme import Scheme
from orangewidget.settings import SettingsPrinter
from silx.gui import qt


class WidgetsSignalManager(_WidgetsSignalManager):
    # skip signal compresion done in original orange version
    def compress_signals(self, signals):
        return signals


class WidgetsScheme(Scheme):
    def __init__(self, parent=None, title=None, description=None, env={}, **kwargs):
        super().__init__(parent, title, description, env=env, **kwargs)
        self.widget_manager = WidgetManager()
        self.signal_manager = WidgetsSignalManager(self)
        self.widget_manager.set_scheme(self)
        self.__report_view = None  # type: Optional[OWReport]
        self.set_loop_flags(self.AllowLoops)

    def widget_for_node(self, node):
        """
        Return the OWBaseWidget instance for a `node`.
        """
        return self.widget_manager.widget_for_node(node)

    def node_for_widget(self, widget):
        """
        Return the SchemeNode instance for the `widget`.
        """
        return self.widget_manager.node_for_widget(widget)

    def sync_node_properties(self):
        """
        Sync the widget settings/properties with the SchemeNode.properties.
        Return True if there were any changes in the properties (i.e. if the
        new node.properties differ from the old value) and False otherwise.

        """
        changed = False
        for node in self.nodes:
            settings = self.widget_manager.widget_settings_for_node(node)
            if settings != node.properties:
                node.properties = settings
                changed = True
        return changed

    def show_report_view(self):
        inst = self.report_view()
        inst.show()
        inst.raise_()

    def has_report(self):
        """
        Does this workflow have an associated report

        Returns
        -------
        has_report: bool
        """
        return self.__report_view is not None

    def report_view(self):
        """
        Return a OWReport instance used by the workflow.

        Returns
        -------
        report : OWReport
        """
        return None

    def set_report_view(self, view):
        """
        Set the designated OWReport view for this workflow.

        Parameters
        ----------
        view : Optional[OWReport]
        """
        self.__report_view = None

    def dump_settings(self, node):
        widget = self.widget_for_node(node)

        pp = SettingsPrinter(indent=4)
        pp.pprint(widget.settingsHandler.pack_data(widget))

    def event(self, event):
        if event.type() == qt.QEvent.Close:
            if self.__report_view is not None:
                self.__report_view.close()
            self.signal_manager.stop()
        return super().event(event)
