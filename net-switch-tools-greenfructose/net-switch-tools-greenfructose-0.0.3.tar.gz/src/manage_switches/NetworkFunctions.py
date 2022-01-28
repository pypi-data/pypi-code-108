import ipaddress
import socket


def generate_ip_list(ip_range: str) -> list[str]:
    """
    Creates a list of IP addresses from provided CIDR range.
    :param ip_range: IP range in CIDR notation
    :return: list of IP addresses as strings
    """
    return [str(ip) for ip in ipaddress.IPv4Network(ip_range)]


def get_hostname_by_ip(ip: str) -> str:
    """
    Gets hostname by IP address.
    :param ip: IP to check as string.
    :return: Either the hostname as a string or 'Hostname not found'
    """
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return 'Hostname not found'
