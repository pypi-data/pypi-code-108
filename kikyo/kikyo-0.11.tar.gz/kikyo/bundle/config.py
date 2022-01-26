from kikyo import Kikyo

from kikyo.bundle.datahub import PulsarBasedDataHub
from kikyo.bundle.oss import MinioBasedOSS, AliyunOSS
from kikyo.bundle.search import EsBasedSearch


def configure_kikyo(client: Kikyo):
    PulsarBasedDataHub(client)
    MinioBasedOSS(client)
    AliyunOSS(client)
    EsBasedSearch(client)
