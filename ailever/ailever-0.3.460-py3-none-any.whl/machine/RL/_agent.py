from abc import ABCMeta, abstractmethod
 
class BaseAgent(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def _setup_policy(self):
        pass

    @abstractmethod
    def _setup_Q(self):
        pass

    @abstractmethod
    def set_agent(self):
        pass

    @abstractmethod
    def micro_update_Q(self):
        pass
 
    @abstractmethod
    def macro_update_Q(self):
        pass

    @abstractmethod
    def judge(self):
        pass

