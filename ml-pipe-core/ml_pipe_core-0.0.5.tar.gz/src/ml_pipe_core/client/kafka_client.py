from typing import List
import json
import time
import requests

from ..topics import CONTROL_TOPIC
from ..config import KAFKA_SERVER_URL, OBSERVER_URL, REGISTER_URL
from ..topics import RECONFIG_TOPIC, SERVICE_INPUT_TOPIC
from ..simple_service_message import SimpleServiceMessage
from ..agent_result_message import AgentResultMessage
from ..message import Headers, ControlMessage
from ..event_utls.producer import Producer
from ..utils.utils import generate_unique_id, wait_until_server_is_online
from ..logger import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class KafkaPipeClient():
    def __init__(self, kafka_broker_url: str = KAFKA_SERVER_URL) -> None:
        self.kafka_broker_url = kafka_broker_url
        self.cc_producer = Producer(kafka_broker_url)
        wait_until_server_is_online(REGISTER_URL, _logger)
        wait_until_server_is_online(OBSERVER_URL, _logger)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        pass

    def wait_for_services(self, names: List[str], timeout: float = 30, sleep_time: float = 0.1, option='start', status=None):
        expected_len = 0 if option == 'shutdown' else len(names)

        t = 0.0
        names_to_be_found = set(names)
        while(t < timeout):
            name_type_set = self.get_service_type_and_name_set(status=status)
            print(f"services: {name_type_set}")

            if len(names_to_be_found.intersection(name_type_set)) == expected_len:
                return True
            time.sleep(sleep_time)
            t += sleep_time
        return False

    def run_service(self, service_type, params=None):

        package_id = generate_unique_id()

        self.cc_producer.sync_produce(topic=SERVICE_INPUT_TOPIC,
                                      value=SimpleServiceMessage(params=params).serialize(),
                                      headers=Headers(package_id=package_id, source='console', only_for=[service_type]))

        return package_id

    def stop_service(self, name):
        package_id = generate_unique_id()
        msg = ControlMessage(name=name, command='stop')

        self.cc_producer.sync_produce(topic=CONTROL_TOPIC,
                                      value=msg.serialize(),
                                      headers=Headers(package_id=package_id, source='console', only_for=[name]))

    def reconfig(self, names: List[str], config_data: dict):
        self.cc_producer.all_partitions_produce(RECONFIG_TOPIC,
                                                value=json.dumps(config_data),
                                                headers=Headers(source='console', only_for=names,
                                                                msg_type=None))

    def get_running_service_info(self):
        res = requests.get(f'http://{REGISTER_URL}/services/')
        if res.status_code == 200:
            return res.json()['services']
        _logger.error(f"receive error code {res.status_code}.")
        return None

    def get_service_type_and_name_set(self, status=None):
        type_name_hash = set()
        for name, info in self.get_running_service_info().items():
            print(name, info['type'], info['status'])
            if status is None or info['status'] == status:
                type_name_hash.add(name)
                type_name_hash.add(info['type'])
        return type_name_hash

    def get_running_services(self):
        return list(self.get_running_service_info().keys())

    def get_service_objects(self):
        services = []
        for name, infos in self.get_running_service_info().items():
            service_type = infos['type']
            info = infos.get('info')
            type = infos.get('type')
            if not service_type == 'simulation':
                services.append(ServiceClient(name, self, type, info))
            else:
                _logger.debug(f"Ignore type: {infos['type']}")
        return {service.name: service for service in services}

    def get_observation(self, package_id, service_type: str = 'Simulation', timeout=30, poll_time=0.05):
        res = requests.get(f'http://{OBSERVER_URL}/find/{package_id}/{service_type}')
        if res.status_code == 200:
            return res.json()
        time_counter = 0.0
        while(res.status_code == 202):
            time.sleep(poll_time)
            time_counter += poll_time
            res = requests.get(f'http://{OBSERVER_URL}/find/{package_id}/{service_type}')
            if res.status_code == 200:
                return res.json() if service_type == 'Simulation' else AgentResultMessage.from_byte_string(res.json()['data'])
            if time_counter >= timeout:
                _logger.error(f"timeout reached for package_id={package_id} and service_type={service_type}.")
                return None

        _logger.error(f"receive error code {res.status_code}.")
        return None


class ServiceClient():
    def __init__(self, name: str, kafkaPipeClient: KafkaPipeClient, type: str,  info: str) -> None:
        self.pipe = kafkaPipeClient
        self.name = name
        self.info = "No info test." if info == None else info
        self.type = type
        self._last_send_package_id = None

    def reconfig(self, config):
        self.pipe.reconfig(names=[self.name], config_data=config)

    def stop(self):
        self.pipe.stop_service(name=self.name)

    def run(self, params):
        self._last_send_package_id = self.pipe.run_service(self.type, params)

    def observe(self):
        return self.pipe.get_observation(self._last_send_package_id)
