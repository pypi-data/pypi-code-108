from messenger2 import config
import argparse
from PySide2.QtWidgets import QApplication
import sys
from messenger2.databases.database import ServerDatabase
from messenger2.server.gui.server_main import ServerWindow
from messenger2.server.core import Server


def get_parameters(address=None, port=None):
    """
    get parameters from command line
    if there are not in line then use default in config file
    :param address: ip address
    :param port: port
    :return: parameters
    """
    parser = argparse.ArgumentParser(description="server parser")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=config.SERVER_PORT,
        help="port name")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        default=config.LISTEN_ADDRESS,
        help="address name")
    args = parser.parse_args()

    if address is None:
        address_param = args.address
    else:
        address_param = address

    if port is None:
        port_param = args.port
    else:
        port_param = port

    return address_param, port_param


def start(ip=None, port=None):
    """
    start server with ip and port
    :param ip: ip address
    :param port: port
    :return: None
    """
    ip, port = get_parameters(ip, port)
    app = QApplication()
    database = ServerDatabase(engine=config.DATABASE_ENGINE)
    core = Server(address=ip, port=port)
    core.setDaemon(True)
    core.start()
    window = ServerWindow(database=database, core=core)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start()
