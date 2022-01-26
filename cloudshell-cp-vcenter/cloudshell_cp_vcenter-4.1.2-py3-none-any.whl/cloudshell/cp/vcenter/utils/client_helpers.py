import atexit
import ssl

from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim  # noqa

from cloudshell.cp.vcenter.exceptions import LoginException


def _get_si_tls_v1(host: str, user: str, password: str, port: int):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    return SmartConnect(
        host=host,
        user=user,
        pwd=password,
        port=port,
        sslContext=context,
    )


def _get_si_tls_v1_2(host: str, user: str, password: str, port: int):
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE
    return SmartConnect(
        host=host,
        user=user,
        pwd=password,
        port=port,
        sslContext=context,
    )


def _get_si_without_ssl(host: str, user: str, password: str, port: int):
    return SmartConnect(
        host=host,
        user=user,
        pwd=password,
        port=port,
    )


def get_si(host: str, user: str, password: str, port: int = 443):
    funcs = (_get_si_tls_v1_2, _get_si_tls_v1, _get_si_without_ssl)
    for func in funcs:
        try:
            si = func(host, user, password, port)
        except (ssl.SSLEOFError, vim.fault.HostConnectFault, ssl.SSLError, OSError):
            continue
        except vim.fault.InvalidLogin:
            raise LoginException("Cannot connect to the vCenter. Invalid user/password")
        else:
            atexit.register(Disconnect, si)
            break
    else:
        raise LoginException("Cannot login with TLSv1_2, TLSv1 and without ssl")
    return si
