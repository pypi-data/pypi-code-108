import os
from playsound import playsound
from tkinter import simpledialog
from tkinter import scrolledtext
import tkinter.ttk as ttk
import tkinter as tk
import socket as st


class MessengerWindow(tk.Tk):
    """
    Window
    """
    # from .widgets import widgetmaking, makeMessageWidgets, usernamewidget, makeIPFrame, deleteinvIPLabel, checkIPEntry, validmessage, validusername, validIP, configuregridweight, makeTopMost, windowsettings
    from .widgets import Widgets, Settings
    from ..netw import startlistening, listenformsg, Message, sendmessage, send

    def __init__(self, port: int, serversocket: st.socket) -> None:
        self.port = port
        # Ausführen der Init-Funktion von Tk(), also dem Window
        super(MessengerWindow, self).__init__()

        self.me = self
        self.settings = self.Settings(self.me)
        self.widg = self.Widgets(self.me)
        # Eigenschaftens
        self.settings.windowsettings()

        # Erschaffen der Widgets etc.
        self.widg.widgetmaking(port)

        self.serversocket = serversocket
        self.startlistening()

    def play(self) -> None:
        sound = os.path.join(os.path.dirname(__file__), "sound.wav")
        playsound(sound, block=False)
        return

    @property
    def user_IP(self) -> str:
        return self.ip_Entry_1.get() + "." + self.ip_Entry_2.get() + "." + self.ip_Entry_3.get() + "." + self.ip_Entry_4.get()


class PortWindow(tk.Tk):
    port: int

    def get_port(self) -> int:
        """\
        Create a simpledialog asking for the port.
        
        If port is None (Dialog was closed) the port is set to 15200
        """
        self.withdraw()
        self.port = simpledialog.askinteger("Port", "What Port?")
        if self.port is None:
            self.port = 15200
        self.destroy()
        return self.port


__all__ = ["MessengerWindow", "PortWindow"]

if __name__ == "__main__":
    print("use __init__.py in messenger folder")
