from abc import ABCMeta, abstractmethod
 
class BaseAgent(metaclass=ABCMeta):
    @abstractmethod
    def update_Q(self):
        pass
 
    @abstractmethod
    def judge(self):
        pass

