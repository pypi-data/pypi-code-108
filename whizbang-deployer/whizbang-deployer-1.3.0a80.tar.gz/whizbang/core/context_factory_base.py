import abc


class IContextFactory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_context(self, context_args, context_type: str):
        """ContextFactory get_context interface"""


class ContextFactoryBase(IContextFactory):
    @abc.abstractmethod
    def get_context(self, context_args, context_type: str):
        """return context"""
