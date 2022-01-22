from time import sleep
from urllib import parse

from ._cpywpa_core import cpw_core
from .cpywpa_error import *


class NetworkManager(cpw_core):
    """
    provide method to control Wi-Fi
    """

    def __init__(self):
        super(NetworkManager, self).__init__()
        # generate information for saved Wi-Fi
        self._generateSavedWiFi()
        # self.Scan()

    def _generateSavedWiFi(self):
        """
        generate saved Wi-Fi information
        :return: dict like:
        {'Wi-Fi id': {'ssid': XXX, 'bssid': XXX:XXX, 'disable': 0(enable) or 1(disable)}}
        """
        # the first line is 'network id / ssid / bssid / flags' which is useless
        _list_networks = self._ListNetworks().split('\n')[1:-1]
        self._saved_wifi = {}
        for _wifi in _list_networks:
            _wifi_information: list = _wifi.split('\t')
            if len(_wifi_information) < 4:
                if _wifi_information[1] == 'any' or ':' in _wifi_information[1]:
                    # if a config don't have ssid, it is waiting for configuration
                    continue
            if _wifi_information[3] == '':
                _wifi_information[3] = 0
            self._saved_wifi[_wifi_information[1]] = {
                'id': str(_wifi_information[0]),
                'ssid': _wifi_information[1],
                'bssid': _wifi_information[2],
                'disable': _wifi_information[3]
            }

    def addNetwork(self, name, passwd, key_mgmt='WPA-PSK', priority=None, bssid='any'):
        """
        add new network config and save it, but doesn't connect.
        to connect to a Wi-Fi, call connect
        :param bssid: Wi-Fi bssid
        :param name: Wi-Fi ssid
        :param passwd: Wi-Fi password
        :param key_mgmt: Wi-Fi accepted authenticated key management protocols
        :param priority: priority tells wpa_supplicant which Wi-Fi it should connect when more than two AP exits
        :return: None if success, and raise error when fail
        """
        # check if parameters is legal
        if '"' in name or '"' in passwd:
            raise ParametersError('" shouldn\'t appear in name or password')
        if name not in self._saved_wifi.keys():
            _network_id = self._AddNetwork().split('\n')[0]
        else:
            _network_id = self._saved_wifi[name]['id']
        if self._SetNetwork(_network_id, 'ssid', '"' + name + '"').split('\n')[0] == 'FAIL':
            raise AddNetworkError('setting value for ssid failed')
        if self._SetNetwork(_network_id, 'psk', '"' + passwd + '"').split('\n')[0] == 'FAIL':
            raise AddNetworkError('setting value for psk failed')
        if self._SetNetwork(_network_id, 'key_mgmt', key_mgmt).split('\n')[0] == 'FAIL':
            raise AddNetworkError('setting value for key_mgmt failed')
        if priority is not None and \
                self._SetNetwork(_network_id, 'priority', priority).split('\n')[0] == 'FAIL':
            raise AddNetworkError('setting value for priority failed')
        if self._SetNetwork(_network_id, 'bssid', bssid).split('\n')[0] == 'FAIL':
            raise AddNetworkError('setting value for bssid failed')
        if self._SaveConfig().split('\n')[0] == 'FAIL':
            raise AddNetworkError('save config failed')
        if self._EnableNetwork(_network_id).split('\n')[0] == 'FAIL':
            raise EnableNetworkError('enable Wi-Fi: {} failed'.format(name))
        self._saved_wifi[name] = {
            'id': _network_id,
            'ssid': name,
            'bssid': bssid,
            'disable': 0
        }

    def connect(self, network_name, passwd=None, key_mgmt='WPA-PSK', priority=None):
        """
        connect to an existed Wi-Fi or a new Wi-Fi
        :param network_name: Wi-Fi ssid
        :param passwd: Wi-Fi password
        :param key_mgmt: Wi-Fi accepted authenticated key management protocols
        :param priority: priority tells wpa_supplicant which Wi-Fi it should connect when more than two AP exits
        :return: None if success, and raise error when fail
        """
        if network_name in self._saved_wifi.keys():
            _network_id = self._saved_wifi[network_name]['id']
            if self._SelectNetwork(_network_id).split('\n')[0] == 'FAIL':
                raise ConnectError('connect to Wi-Fi: {} failed'.format(network_name))
        else:
            if network_name is None or passwd is None:
                raise ConnectError('neither network_name nor new Wi-Fi information is given, can\'t connect')
            else:
                self.addNetwork(name=network_name, passwd=passwd, key_mgmt=key_mgmt, priority=priority)
                _network_id = self._saved_wifi[network_name]['id']
                if self._SelectNetwork(_network_id).split('\n')[0] == 'FAIL':
                    raise ConnectError('connect to Wi-Fi: {} failed'.format(network_name))
        self._generateSavedWiFi()

    def onlyScan(self):
        """
        just as its name, only tell wpa to scan and return nothing
        :return: None
        """
        self._Scan()

    def scan(self, scan_time=8):
        """
        scan Wi-Fi around and wait 8s to get results, if wpa is busy, then sleep 1s and try again and raise BusyError
        after three times
        !!! IMPORTANT !!!
        If you just want wpa to scan, use onlyScan
        :param scan_time: time for wpa to scan Wi-Fi, default 5s
        :return: dict include Wi-Fi information
        """
        _try_time = 3
        _scan_flag = 1
        while _try_time > 1:
            if self._Scan().split('\n')[0] != 'OK':
                sleep(1)
            else:
                _scan_flag = 0
                break
        if _scan_flag:
            if self._Scan().split('\n')[0] != 'OK':
                raise BusyError('wpa is busy! please try later')
        # give wpa time to scan
        sleep(scan_time)
        # the first line is 'bssid / frequency / signal level / flags / ssid'
        scan_results = self._ScanResults().split('\n')[1:]
        wifi_info = []
        _warn_flag = 0
        for _wifi in scan_results:
            _wifi_params: list = _wifi.split('\t')
            if len(_wifi_params) < 5:
                # the info is uncompleted
                continue
            if '\\x' in _wifi_params[-1]:
                # possibly it is Chinese name
                if not _warn_flag:
                    print(
                        '[WARN]: detect string \'\\x\' in ssid, if your Wi-Fi name is in Chinese, please ignore this. '
                        'If your actual Wi-Fi name contains string \'\\x\', then please ignore the wrong name in '
                        'result. However, some unexpected error may occur.')
                    _warn_flag = 1
                _wifi_ssid = _wifi_params[-1].encode('raw_unicode_escape').decode('utf-8')
                _wifi_ssid = parse.unquote(_wifi_ssid.replace('\\x', '%'))
            else:
                _wifi_ssid = _wifi_params[-1]
            wifi_info.append({'ssid': _wifi_ssid, 'bssid': _wifi_params[0]})
        return wifi_info

    def listNetwork(self):
        self._generateSavedWiFi()
        return self._saved_wifi

    def removeNetwork(self, network_name):
        """
        remove a configuration
        :param network_name: network id
        :return: None
        """
        if network_name not in self._saved_wifi.keys():
            raise ParametersError('network name doesn\'t exist')
        if self._RemoveNetwork(self._saved_wifi[network_name]['id']).split('\n')[0] != 'OK':
            raise RemoveError('remove network failed')

    def getStatus(self):
        """
        get wpa status
        :return: information dict
        """
        key_value = self._GetStatus().split('\n')[1:-1]
        status = {}
        for _key_value in key_value:
            key, value = _key_value.split('=')
            status[key] = value
        return status

    def scanResults(self):
        """
        get scan results
        :return: dict including Wi-Fi information
        """
        scan_results = self._ScanResults().split('\n')[1:]
        wifi_info = []
        _warn_flag = 0
        for _wifi in scan_results:
            _wifi_params: list = _wifi.split('\t')
            if len(_wifi_params) < 5:
                # the info is uncompleted
                continue
            if '\\x' in _wifi_params[-1]:
                # possibly it is Chinese name
                if not _warn_flag:
                    print(
                        '[WARN]: detect string \'\\x\' in ssid, if your Wi-Fi name is in Chinese, please ignore this. '
                        'If your actual Wi-Fi name contains string \'\\x\', then please ignore the wrong name in '
                        'result. However, some unexpected error may occur.')
                    _warn_flag = 1
                _wifi_ssid = _wifi_params[-1].encode('raw_unicode_escape').decode('utf-8')
                _wifi_ssid = parse.unquote(_wifi_ssid.replace('\\x', '%'))

            else:
                _wifi_ssid = _wifi_params[-1]
            wifi_info.append({'ssid': _wifi_ssid, 'bssid': _wifi_params[0]})
        return wifi_info
