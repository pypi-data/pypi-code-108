import random
import socket
from aishu import setting


class date(object):
    def getIp(self):
        ipList = ["192.168.84.105",
                  "192.168.84.192",
                  "192.168.84.217",
                  "192.168.84.108",
                  "192.168.84.107",
                  "192.168.84.182",
                  "192.168.84.193",
                  "192.168.84.109",
                  "192.168.84.175",
                  "192.168.84.60",
                  "192.168.84.61",
                  "192.168.84.63",
                  "192.168.84.62",
                  "192.168.84.64",
                  "192.168.84.65",
                  "192.168.84.66"]
        return random.choice(ipList)

    def getAentHostIp(self):
        ip = '10.4.104.197'
        return ip

    def getIpVR(self):
        return '{ip1}.{ip2}.{ip3}.{ip4}'.format(ip1=10, ip2=random.choice(range(10, 250)),
                                                ip3=random.choice(range(10, 250)), ip4=random.choice(range(10, 250)))

    def getIpError(self):
        return '{ip1}.{ip2}.{ip3}.{ip4}'.format(ip1='abc', ip2=random.choice(range(10, 99)),
                                                ip3=random.choice(range(10, 99)), ip4=random.choice(range(10, 99)))

    def getTestHostIP(self):
        return setting.host

    def get_host_ip(self):
        # 获取计算机名称
        hostname = socket.gethostname()

        # 获取本机IP
        host_ip = socket.gethostbyname(hostname)
        return host_ip

    def get_host_name(self):
        # 获取计算机名称
        hostname = socket.gethostname()
        return hostname
