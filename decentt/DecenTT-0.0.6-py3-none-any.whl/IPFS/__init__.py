import subprocess
from DecenTT.IPFS.locales.bootstrap import BStrapper
from DecenTT.IPFS.pubsub import Client
import requests


class Daemon:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self.daemon = self.__start_daemon(**self._kwargs)

    @staticmethod
    def __start_daemon(
            pubsub_mode=True,
            **kwargs
    ):
        if not pubsub_mode:
            return subprocess.Popen(["ipfs", "daemon"], **kwargs)
        return subprocess.Popen(["ipfs", "daemon", "--enable-pubsub-experiment"], **kwargs)

    def stop(self):
        self.daemon.kill()
        _sd_process = subprocess.Popen(["ipfs", "shutdown"])

    def reload(self):
        self.stop()
        self.daemon = self.__start_daemon(**self._kwargs)


class Peer:
    def __init__(self):
        self.details = requests.post(
            f"http://127.0.0.1:5001/api/v0/id"
        ).json()
        self.id = self.details["ID"]
        self.peers = requests.post(
            f"http://127.0.0.1:5001/api/v0/swarm/peers"
        ).json()
        self.bootstraps = requests.post(
            f"http://127.0.0.1:5001/api/v0/bootstrap/list"
        ).json()
        self.bootstrap_peers = set([self.__get_peerId(address=str(x)) for x in self.bootstraps["Peers"]])

    def __get_peerId(self, address: str):
        domain_list = address.split("/")
        return domain_list[-1]
