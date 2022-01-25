# -*- coding: future_fstrings -*-
from sumoappclient.common.mixin import DynamicLoadMixin


class OutputHandlerFactory(DynamicLoadMixin):

    handlers = {
        "HTTP": "outputhandlers.HTTPHandler",
        "CONSOLE": "outputhandlers.STDOUTHandler",
        "FILE": "outputhandlers.FileHandler",
        "CToC": "outputhandlers.CToCHandler"
    }

    @classmethod
    def get_handler(cls, handler_type, *args, **kwargs):

        if handler_type in cls.handlers:
            module_class = cls.load_class(cls.handlers[handler_type],  __name__)
            module_instance = module_class(*args, **kwargs)
            return module_instance
        else:
            raise Exception(f"Invalid OUTPUTHANDLER {handler_type}")