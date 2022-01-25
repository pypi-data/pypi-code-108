import abc


class ICommandBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def command(self):
        """"""
        
    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """"""

    @property
    @abc.abstractmethod
    def command_abbreviation(self) -> str:
        """"""

    @property
    @abc.abstractmethod
    def command_description(self) -> str:
        """"""

class CommandBase(ICommandBase):
    @abc.abstractmethod
    def command(self):
        raise NotImplementedError
        
    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """"""

    @property
    @abc.abstractmethod
    def command_abbreviation(self) -> str:
        """"""

    @property
    @abc.abstractmethod
    def command_description(self) -> str:
        """"""
