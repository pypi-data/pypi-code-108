"""
Python Messenger
Author: Oliver Sader
"""
from .netw import MessengerSocket
from .messengerUI import PortWindow, MessengerWindow
import sys


if __name__ == "__main__":
    serversocket = MessengerSocket()
    bound = False
    while not bound:
        if len(sys.argv) == 1:
            port = PortWindow().get_port()
        else:
            try:
                int(sys.argv[1])
            except ValueError:
                raise SystemExit(
                    'Usage: Messenger.py <Port: int> [Port must be integer!]')
            else:
                port = sys.argv[1]
        try:
            serversocket.bind(("", port))
        except:
            pass
        else:
            bound = True
        root = MessengerWindow(port, serversocket)
        root.focus_force()
        root.mainloop()
