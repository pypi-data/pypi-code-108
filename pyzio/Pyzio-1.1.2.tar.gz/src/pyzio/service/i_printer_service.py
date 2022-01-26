from abc import ABCMeta, abstractmethod


class IPrinterService(metaclass=ABCMeta):
    @abstractmethod
    def load_printer(self):
        pass

    @abstractmethod
    def dump_printer(self):
        pass

    @abstractmethod
    def is_printer_paired(self):
        pass

    @abstractmethod
    def get_sensors(self):
        pass

    @abstractmethod
    def get_sensor_by_name(self, name):
        pass

    @abstractmethod
    def add_sensor(self, name, phasio_id, sensor_type):
        pass

    @abstractmethod
    def get_printer_id(self):
        pass

    @abstractmethod
    def set_printer_id(self, printer_id):
        pass

    @abstractmethod
    def get_candidate_id(self):
        pass

    @abstractmethod
    def set_candidate_id(self, candidate_id):
        pass

    @abstractmethod
    def set_secret(self, secret):
        pass

    @abstractmethod
    def get_secret(self):
        pass

    @abstractmethod
    def set_pairing_code(self, pairing_code):
        pass

    @abstractmethod
    def get_pairing_code(self):
        pass

    @abstractmethod
    def register_candidate(self, printer_name, printer_model, printer_material, file_type):
        pass