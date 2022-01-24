import grpc
from .api import Api


class Grpc(Api):

    def __init__(self, host):
        super().__init__()
        self.channel = grpc.insecure_channel(host)

    def get_grpc(self, api_id):
        pb2, pb2_grpc = grpc.protos_and_services(self.get_api(api_id))



