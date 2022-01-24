from abc import ABCMeta, abstractmethod


class AbstractChannel(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def notif_type():
        raise NotImplementedError()

    @abstractmethod
    def json(self):
        raise NotImplementedError()

    @abstractmethod
    def attachments(self):
        raise NotImplementedError()
