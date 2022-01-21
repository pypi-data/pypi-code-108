import socket
from pushover import init, Client


class Notifier:
    def __init__(self, title=None, token=None, userkey=None):
        self.title = title
        init(token)
        ip = get_ip_address()
        if self.title is None:
            self.title = ip
        self.client = Client(userkey)
        self.client.send_message("My IP address:\n"+ip, title=self.title)

    def info_message(self, message):
        self.client.send_message(message, title=self.title + " info")

    def alert_message(self, message):
        self.client.send_message(message, title=self.title + " ALERT")


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
