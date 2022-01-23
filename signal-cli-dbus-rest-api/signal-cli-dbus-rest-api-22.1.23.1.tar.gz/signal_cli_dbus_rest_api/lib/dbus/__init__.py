"""
DBus connection for signal-cli
"""

from pydbus import SystemBus as pydbusSystemBus
from dbus import SystemBus as dbusSystemBus


class SignalCLIDBus():  # pylint: disable=too-few-public-methods
    """
    DBus connection for signal-cli
    """

    def __init__(self, **kwargs):
        """
        initialize DBus connection
        """
        self.connection = None
        self.pydbus = pydbusSystemBus()
        self.dbus = dbusSystemBus()
        objectpath = None
        if kwargs.get("number"):
            number_escape = (
                str(kwargs.get("number")).encode().decode("unicode_escape").strip("+")
            )
            objectpath = f"/org/asamk/Signal/_{number_escape}"
        if kwargs.get("account"):
            objectpath = kwargs.get("account")
        if objectpath:
            self.pydbusconn = self.pydbus.get(
                "org.asamk.Signal",
                objectpath,
            )
            self.dbusconn = self.dbus.get_object(
                "org.asamk.Signal",
                objectpath,
            )
        else:
            self.pydbusconn = self.pydbus.get("org.asamk.Signal")
            self.dbusconn = self.dbus.get_object("org.asamk.Signal", "/org/asamk/Signal")
