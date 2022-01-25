from typing import List, Optional, Dict
from zappix.protocol import ActiveChecksRequest, AgentDataRequest, ModelEncoder, ActiveItem
from zappix.dstream import _Dstream
import json
import logging

logger = logging.getLogger(__name__)


class AgentActive(_Dstream):
    """
    Class for getting active check configuration for a host from Zabbix Server
    and sending collected data.

    Parameters
    ----------
    :host:
        Technical hostname as configured in Zabbix.
    :server:
        IP address of target Zabbix Server.
    :server_port:
        Port on which the Zabbix Server listens.
    :source_address:
        Source IP address.
    """

    def __init__(self, host: str, server: str, server_port: int = 10051, source_address: Optional[str] = None) -> None:
        super().__init__(server, server_port, source_address)
        self._host = host

    def get_active_checks(self) -> List[ActiveItem]:
        """
        Gets list of active checks for host.

        Returns
        -------
        list
            List of ActiveItem objects.
        """
        request = ActiveChecksRequest(self._host)
        logger.info(f"Getting active checks for host: {self._host} from: {self._ip}:{self._port}")
        result = self._send(request.to_bytes())
        return self._parse_active_check_list(result)

    def send_collected_data(self, data: AgentDataRequest) -> Optional[Dict]:
        """
        Sends collected data to Zabbix.

        Parameters
        ----------
        :data:
            Instance of AgentDataRequest.

        Returns
        -------
        list
            List of ActiveItem objects.
        """
        if not isinstance(data, AgentDataRequest):
            logger.error(f"Object {data} is not an instance AgentDataRequest")
            raise ValueError
        result = self._send(data.to_bytes())
        return self._parse_server_response(result)

    @staticmethod
    def _parse_active_check_list(data: str) -> List[ActiveItem]:
        response = json.loads(data)
        active_list_raw = response.get('data', [])
        active_list = [ActiveItem(
                item['key'], item['delay'], item['lastlogsize'], item['mtime']
                ) for item in active_list_raw]
        return active_list
