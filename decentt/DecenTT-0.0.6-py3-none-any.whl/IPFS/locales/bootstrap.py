import os.path

from DecenTT.IPFS.locales.env_config import getBootstrapNodes
import requests
from DecenTT.IPFS.locales.IPFSLocalesExceptions import *
from DecenTT.IPFS.logger import logger


class BStrapper:
    """
    >>> bstrapper = BStrapper()
    >>> # bstrapper.add("/dnsaddr/bootstrap.libp2p.io/p2p/QmcZf59bWwK5XFi76CZX8cbJ4BhTzzA3gU1ZjYZcYW3dwt")
    >>> bstrapper.load_all()
    """

    def __init__(self, path: str = None) -> None:
        self.__env_path = path

    def add(self, address: str):
        valid = self.__validate(address)
        if valid:
            resp = requests.post(
                f"http://127.0.0.1:5001/api/v0/bootstrap/add?arg={address}"
            )
            logger.info(f"Bootstrap Addition Response: {resp}")
            logger.info(f"Bootstrap Added : {address}")
        else:
            raise InvalidBootstrap

    def get_peerId(self, address: str):
        domain_list = address.split("/")
        return domain_list[-1]

    def record(self, address: str):
        valid = self.__validate(address=address)
        if valid:
            bs_list = getBootstrapNodes(self.__env_path)
            last_index = len(bs_list)
            file_path = os.path.dirname(os.path.realpath(__file__))
            with open(f"{file_path}/.env", 'ab') as f:
                f.write(f"BOOTSTRAP_{last_index}={address}\n")

    def load_all(self):
        bs_list = getBootstrapNodes(self.__env_path)
        for bs in bs_list:
            self.add(address=bs)

    def __validate(self, address: str) -> bool:
        peerId = self.get_peerId(address=address)
        seg_len = len(address.split("/"))

        if peerId == "" or seg_len < 2:
            return False
        return True
