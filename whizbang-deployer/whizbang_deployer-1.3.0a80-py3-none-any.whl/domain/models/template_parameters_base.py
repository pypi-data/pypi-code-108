from abc import abstractmethod

from whizbang.domain.models.json_serializable import JsonSerializable


class TemplateParametersBase(JsonSerializable):
    @abstractmethod
    def __init__(self):
        super().__init__()


