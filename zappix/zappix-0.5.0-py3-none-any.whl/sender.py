"""
Python implementation of Zabbix sender.
"""

from typing import List, Any, Optional, Dict, Tuple, Callable, Union, Optional
from zappix.dstream import _Dstream
from zappix.protocol import SenderData, SenderDataRequest
import csv
import time
import functools
import logging

logger = logging.getLogger(__name__)


class Sender(_Dstream):
    """
    Class implementing zabbix_sender utility.

    Parameters
    ----------
    :server:
        IP address of target Zabbix Server.
    :port:
        Port on which the Zabbix Server listens.
    :source_address:
        Source IP address.
    """

    def __init__(self, server: str, port: int = 10051, source_address: Optional[str] = None) -> None:
        super().__init__(server, port, source_address)

    def send_value(self, host: str, key: str, value: Any) -> Union[Dict[str, Any], None]:
        """
        Send a single value to a Zabbix host.

        Parameters
        ----------
        :host:
            Name of a host as visible in Zabbix frontend.
        :key:
            String representing an item key.
        :value:
            Value to be sent.

        Returns
        -------
        dict
            Information from server.
        """
        payload = SenderDataRequest()
        payload.add_item(SenderData(host, key, value))

        response = self._send(payload.to_bytes())
        parsed_response = self._parse_server_response(response)
        return parsed_response if parsed_response else None

    def send_file(self, file: str, with_timestamps: bool = False) -> Tuple[Optional[Dict], List[int]]:
        """
        Send values contained in a file to specified hosts.

        Parameters
        ----------
        :file:
            Path to file with data.
        :with_timestamps:
            Specify whether file contains timestamps for items.

        Returns
        -------
        dict
            Information from server.
        """
        items, corrupted_lines = self.parse_data_file(file, with_timestamps)
        payload = SenderDataRequest(items)

        if with_timestamps:
            now = time.time()
            payload.clock = int(now//1)
            payload.ns = int(now % 1 * 1e9)

        response = self._send(payload.to_bytes())
        return self._parse_server_response(response), corrupted_lines

    def send_result(self, host: str, key: str) -> Any:
        """
        Decorator that sends a functions resoult to specified key on a host.

        Parameters
        ----------
        :host:
            Name of a host as visible in Zabbix frontend.
        :key:
            String representing an item key.

        Returns
        -------
        dynamic
            Result of decorated function.
        """
        def wrap_function(func: Callable) -> Callable:
            @functools.wraps(func)
            def get_value(*args, **kwargs):
                result = func(*args, **kwargs)
                self.send_value(host, key, str(result))
                return result
            return get_value
        return wrap_function

    def send_bulk(self, request: SenderDataRequest, with_timestams: bool = False) -> Optional[Dict]:
        """
        Send item values to Zabbix in bulk.

        Parameters
        ----------
        :request:
            Path to file with data.
        :with_timestamps:
            Specify whether SenderData objects contain timestamps.

        Returns
        -------
        dict
            Information from server.
        """
        if with_timestams:
            now = time.time()
            request.clock = int(now//1)
            request.ns = int(now % 1 * 1e9)

        response = self._send(request.to_bytes())
        return self._parse_server_response(response)

    @staticmethod
    def parse_data_file(file: str, with_timestamps: bool = False) -> Tuple[List[SenderData], List[int]]:
        items = []
        failed_lines = []
        try:
            with open(file, 'r', encoding='utf-8') as values:
                reader = csv.reader(values, delimiter=' ', skipinitialspace=True)
                logger.info(f"Reading data from {file}")

                for row in reader:
                    if not all(row):
                        failed_lines.append(reader.line_num)
                        logger.error(f"Found corrupted line in {file} at row {reader.line_num}")
                        continue
                    try:
                        if with_timestamps:
                            data = SenderData(row[0], row[1], row[3], int(row[2]))
                        else:
                            data = SenderData(row[0], row[1], row[2])
                        items.append(data)
                        logger.debug(f"Adding {data} to Sender payload")
                    except (IndexError, ValueError):
                        failed_lines.append(reader.line_num)
                        logger.exception(f"Could not parse {file} at line {reader.line_num}")
        except EnvironmentError:
            logger.exception(f'Error while reading file: {file}')
        finally:
            return items, failed_lines


if __name__ == '__main__':
    import argparse
    params = argparse.ArgumentParser()
    params.add_argument('-z', '--zabbix', nargs='?')
    params.add_argument('-p', '--port', nargs='?', default=10051, type=int)
    params.add_argument('-I', '--source-address', nargs='?')
    params.add_argument('-s', '--host', nargs='?')
    params.add_argument('-k', '--key', nargs='?')
    params.add_argument('-o', '--value', nargs='?')
    params.add_argument('-i', '--input-file', nargs='?')
    params.add_argument('-T', '--with-timestamps', action='store_true')
    args = params.parse_args()

    if args.source_address:
        zab = Sender(args.zabbix, args.port, args.source_address)
    else:
        zab = Sender(args.zabbix, args.port)

    if all([args.host, args.key, args.value]):
        result = zab.send_value(args.host, args.key, args.value)
    elif args.input_file:
        result, corrupted_lines = zab.send_file(args.input_file, True if args.with_timestamps else False)

    print('info from server: "{}"'.format(result))
