from divinegift import logger
from divinegift.errors import SenderNotInitializedError

try:
    from pyzabbix import ZabbixMetric, ZabbixSender
except ImportError:
    raise ImportError("py-zabbix isn't installed. Run: pip install -U py-zabbix")


class ZabbixAgent:
    def __init__(self, zabbix_server=None, zabbix_port=10051):
        self.sender = None
        self.sender = self.init_sender(zabbix_server, zabbix_port) if zabbix_server is not None else None

    def init_sender(self, zabbix_server, zabbix_port=10051):
        if self.sender is None:
            return ZabbixSender(zabbix_server, zabbix_port)
        else:
            return self.sender

    def send(self, host, key, value):
        if self.sender is None:
            raise SenderNotInitializedError('Initialize sender first!')

        try:
            result = self.sender.send([ZabbixMetric(host=host, key=key, value=value)])
        except Exception as ex:
            result = {}
        logger.get_logger().log_debug(result)
        return result
