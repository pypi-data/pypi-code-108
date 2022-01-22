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
                print(int(sys.argv[1]))
                int(sys.argv[1])
            except ValueError:
                raise SystemExit(
                    'Usage: Messenger.py <Port: int> [Port must be integer!]')
            else:
                port = int(sys.argv[1])
                print(port)
        try:
            print("binding...")
            serversocket.bind(("", port))
        except Exception as e:
            print(e)
            sys.exit()
        else:
            bound = True
            print("================================")
            print("bound")
            print("================================")
        finally:
            print("try except finished")
        root = MessengerWindow(port, serversocket)
        root.focus_force()
        root.mainloop()
