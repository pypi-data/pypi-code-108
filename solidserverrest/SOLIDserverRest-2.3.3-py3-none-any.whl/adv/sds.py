# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 14:23:12 alex>
#
# only for python v3

"""
SOLIDserver management server access
"""

import logging
import ipaddress
import socket

from json.decoder import JSONDecodeError

from SOLIDserverRest.Exception import SDSInitError, SDSAuthError
from SOLIDserverRest.Exception import SDSEmptyError
from SOLIDserverRest import SOLIDserverRest

from .class_params import ClassParams

__all__ = ["SDS"]


# more than 7 arguments to class
# pylint: disable=R0902
class SDS(ClassParams):
    """ class to get connected to a SDS server """

    # ---------------------------
    def __init__(self, ip_address=None, user=None, pwd=None):
        """init the SDS object:
        """
        super().__init__()

        self.sds_ip = None
        if ip_address is not None:
            # is the ip_address an IPv4 one?
            try:
                ipaddress.IPv4Address(ip_address)
                self.set_server_ip(ip_address)
            except ipaddress.AddressValueError:
                self.set_server_name(ip_address)

        self.user = None
        self.pwd = None
        if user is not None and pwd is not None:
            self.set_credentials(user, pwd)

        self.version = None

        self.auth_method = None
        self.check_certificate = False

        self.sds = None
        self.timeout = 1

        self.proxy_socks = None

    # ---------------------------
    def set_server_ip(self, ip_address):
        """set the SOLIDserver IP address for the connection"""
        try:
            ipaddress.IPv4Address(ip_address)
        except ipaddress.AddressValueError as error:
            raise SDSInitError(message=f"IPv4 address of"
                               " server error: {error}") from error

        self.sds_ip = ip_address

    # ---------------------------
    def set_server_name(self, fqdn):
        """set the SOLIDserver FQDN for the connection"""
        # check that the IP exists
        try:
            _ = socket.gethostbyname(fqdn)
        except socket.gaierror as error:
            raise SDSInitError(message=f"FQDN of the SDS: {error}") from error

        self.sds_ip = fqdn

    # ---------------------------
    def set_proxy_socks(self, proxy=None):
        """set the SOLIDserver connection through a socks proxy"""
        if proxy:
            self.proxy_socks = proxy

    # ---------------------------
    def set_credentials(self, user=None, pwd=None):
        """add user and login to credentials of this session"""
        if user is None or pwd is None:
            msg = "missing user or password in credentials"
            raise SDSInitError(message=msg)
        self.user = user
        self.pwd = pwd

    # ---------------------------
    def connect(self, method="basicauth", cert_file_path=None, timeout=1):
        """connects to SOLIDserver and check everything is OK by
           querying the version of the admin node in the member list

           method -- basicauth (default) or native (header based)
           cert_file_path -- disable SSL check if None (default)
                             file with cert if check enabled
        """
        if self.user is None or self.pwd is None:
            msg = "missing user or password in credentials for connect"
            raise SDSInitError(message=msg)
        if self.sds_ip is None:
            raise SDSInitError(message="missing ip for server for connect")

        self.sds = SOLIDserverRest(self.sds_ip)

        if method == "basicauth":
            self.sds.use_basicauth_sds(self.user, self.pwd)
            self.auth_method = "basic auth"
        elif method == "native":
            self.sds.use_native_sds(self.user, self.pwd)
            self.auth_method = "native"

        # certificate & SSL check
        if cert_file_path is not None:
            self.sds.set_certificate_file(cert_file_path)
            self.check_certificate = True
        else:
            self.sds.set_ssl_verify(False)

        if timeout != self.timeout:
            self.timeout = timeout

        if self.proxy_socks:
            self.sds.set_proxy(self.proxy_socks)

        self.version = self.get_version()

        if self.version is None:   # pragma: no cover
            self.version = "ukn"
            # need to check if a simple call to a space api is working

    # ---------------------------
    def disconnect(self):
        """disconnects from the SOLIDserver"""
        self.sds = None
        self.version = None
        self.sds_ip = None
        self.user = None
        self.pwd = None
        self.auth_method = None
        self.check_certificate = False
        self.timeout = 1

    # ---------------------------
    def get_version(self):
        """get software version of the SDS based on the management platform
        returns version as a string
        """

        if self.sds is None:
            raise SDSEmptyError(message="not connected")

        if self.version is not None:
            return self.version

        j = self.query("member_list",
                       params={
                           'WHERE': 'member_is_me=1',
                       },
                       option=False)

        if j is None:   # pragma: no cover
            logging.error("error in getting answer on version")
            return None

        if 'member_is_me' not in j[0]:   # pragma: no cover
            logging.error("error in getting version")
            return None

        self.version = j[0]['member_version']
        return self.version

    # ---------------------------
    def get_load(self):
        """get cpu, mem, io"""
        if self.sds is None:
            raise SDSEmptyError(message="not connected")

        j = self.query("member_list",
                       params={
                           'WHERE': 'member_is_me=1',
                       },
                       option=False)

        if j is None:   # pragma: no cover
            logging.error("error in getting answer on version")
            return None

        return {
            'cpu': float(j[0]['member_snmp_cpuload_percent']),
            'ioload': int(j[0]['member_snmp_ioload']),
            'mem': int(j[0]['member_snmp_memory']),
            'hdd': int(j[0]['member_snmp_hdd']),
        }

    # ---------------------------
    def query(self, method, params='', option=False, timeout=1):
        """execute a query towards the SDS"""

        if self.sds is None:
            raise SDSEmptyError(message="not connected")

        _timeout = self.timeout
        if timeout not in (self.timeout, 1):
            _timeout = timeout

        try:
            answer_req = self.sds.query(method,
                                        params=params,
                                        option=option,
                                        timeout=_timeout)

            if answer_req.status_code == 401:   # pragma: no cover
                raise SDSAuthError(message="authentication error")

            if answer_req.status_code == 204:
                raise SDSEmptyError(message="204 returned")

            try:
                j = answer_req.json()
                return j
            except JSONDecodeError:   # pragma: no cover
                logging.error("no json in return")
                return None

        except SDSAuthError as error:   # pragma: no cover
            raise SDSAuthError(f"{error}") from error

    # ---------------------------
    def __str__(self):
        """return the string notation of the server object"""
        connected = "not connected"
        if self.version:
            connected = (f"connected version={self.version}"
                         + f" auth={self.auth_method}")
        proxy = ""
        if self.proxy_socks:
            proxy = f" socks5h://{self.proxy_socks}"

        return (f"sds ip={self.sds_ip}{proxy}"
                " cred={self.user} {connected} [{self.sds}]")
