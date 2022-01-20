from threading import Thread, Event
from RainbowMonitoringSDK.utils.basics import ThreadSafeDict


class Exporter(Thread):

    def __init__(self, name):
        super(Exporter, self).__init__(name=name)
        self.name = name
        # exporter's status initialized as inactive
        self.exporter_status = ExporterStatus.INACTIVE
        # DO NOT MESS WITH: threading lock/event handle state transition
        self._activateEvent = Event()
        # flag to test if first time Exporter activated
        self._first = True

    def activate(self):
        """
        Starts the extractor thread (if this is required)
        :return:
        """
        if self.get_exporter_status() == ExporterStatus.INACTIVE:
            # only want to start the thread once
            if self._first:
                self.start()
                self._first = False
            # thread you can now 'unpause'
            self._activateEvent.set()
            self.exporter_status = ExporterStatus.ACTIVE

    def deactivate(self):
        # if exporter is already INACTIVE, no need to do anything
        if self.get_exporter_status() == ExporterStatus.ACTIVE:
            # thread you are now 'magically' paused
            self._activateEvent.clear()
            self.exporter_status = ExporterStatus.INACTIVE

    def terminate(self):
        if not self._activateEvent.isSet():
            self._activateEvent.set()
        self.exporter_status = ExporterStatus.TERM

    def dissemination_rate_adjustment(self, data: dict):
        # TODO dissemination adaptiveness
        return data

    def update(self, data: dict):
        """
        Updates (prunes) the data based on specific logic (adaptive dissemination)
        :param data:
        :return:
        """
        if self.exporter_status == ExporterStatus.ACTIVE:
            data = self.dissemination_rate_adjustment(data)
        return data

    def run(self):
        pass

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_exporter_status(self):
        """method that returns probe status... INACTIVE, ACTIVE, TERM
        """
        return self.exporter_status

    def set_exporter_status(self, status):
        if ExporterStatus.__contains__(status):
            self.exporter_status = status
        else:
            raise CatascopiaExporterStatusException('Exporter ' + self.name + ', attempted to set invalid status')


class ExporterStatus:
    typeNum = 3
    INACTIVE, ACTIVE, TERM = range(3)
    _typeStrings = {0: 'INACTIVE',
                    1: 'ACTIVE',
                    2: 'TERM'
                    }

    @staticmethod
    def __contains__(t):
        return False if (t not in range(ExporterStatus.typeNum)) else True

    @staticmethod
    def type_as_string(t):
        return ExporterStatus._typeStrings.get(t)


class CatascopiaExporterStatusException(Exception):
    pass
