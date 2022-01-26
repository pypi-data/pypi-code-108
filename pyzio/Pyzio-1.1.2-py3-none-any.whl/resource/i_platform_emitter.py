from abc import ABCMeta, abstractmethod


class IPlatformEmitter(metaclass=ABCMeta):
    @abstractmethod
    def set_listener(self, listener):
        pass

    @abstractmethod
    def connect_as_printer(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_mqtt_connected(self):
        pass

    @abstractmethod
    def send_sensor_registration(self, sensor_name, sensor_type):
        pass

    @abstractmethod
    def mark_job_failed(self, job_id):
        pass

    @abstractmethod
    def mark_job_complete(self, job_id, filepath):
        pass

    @abstractmethod
    def mark_job_in_progress(self, job_id):
        pass

    @abstractmethod
    def send_sensor_update(self, sensor_id, value, sensor_type):
        pass

    @abstractmethod
    def register_candidate(self):
        pass
