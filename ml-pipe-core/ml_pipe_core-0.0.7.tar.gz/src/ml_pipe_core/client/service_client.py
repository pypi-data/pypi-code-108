from typing import List
from .kafka_client import KafkaPipeClient, ServiceId


class ServiceClient():
    def __init__(self, pipe_client: KafkaPipeClient, names: List[str], type: str,  info: str) -> None:
        self.pipe = pipe_client
        self.info = "No info test." if info == None else info
        self.type = type
        self.names = names

    def stop(self, names=None):
        supspending_services = self.names if names is None else names
        for name in supspending_services:
            self.pipe.stop_service(name)


class MachineClient(ServiceClient):
    def __init__(self, names: List[str], pipe_client: KafkaPipeClient, type: str,  info: str) -> None:
        super().__init__(pipe_client, names, type, info)

    def is_processed(self, service_id: ServiceId):
        return False if self.pipe.wait_for_simulation(service_id, self.type) is None else True


class AgentClient(ServiceClient):
    def __init__(self, pipe_client: KafkaPipeClient, names: List[str], type: str,  info: str) -> None:
        super().__init__(pipe_client, names, type, info)
        self._service_id = None

    def reconfig(self, config):
        self.pipe.reconfig(names=[self.type], config_data=config)

    def run(self, params=None):
        self._service_id = self.pipe.run_service(self.type, params)
        return self._service_id

    def get_result(self):
        return self.pipe.get_service_results(self._service_id)
