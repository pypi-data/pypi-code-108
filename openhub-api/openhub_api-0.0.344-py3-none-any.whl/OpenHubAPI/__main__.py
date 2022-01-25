import socket

from .manage.manage import main


def get_my_ip():
    """
    Find my IP address
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


ip = str(get_my_ip())

main('__main__.py','makemigrations', 'data')
main('__main__.py','migrate', 'data')
main('__main__.py','makemigrations')
main('__main__.py','migrate')
main('__main__.py','runserver',ip + ':8000')
