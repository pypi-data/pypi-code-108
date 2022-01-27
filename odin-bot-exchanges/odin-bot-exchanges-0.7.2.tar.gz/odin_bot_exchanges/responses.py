from abc import ABC, abstractmethod


class AbstractResponseParser(ABC):
    @abstractmethod
    def parse_response(self, response: dict, **kwargs):
        pass
