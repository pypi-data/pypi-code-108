import dis
import types
from messenger2.common.decorators import log_exception


class BaseVerifier(type):
    """
    Base metaclass.
    Contains static methods.
    """
    def __init__(cls, name, bases, attr):
        super(BaseVerifier, cls).__init__(name, bases, attr)

    @staticmethod
    @log_exception(Exception)
    def start_verify(attr, prohibited_params, necessary_params):
        necessary_params_count = 0
        for key, value in attr.items():
            # print(value)
            try:
                closures = value.__closure__
                if closures is not None:
                    # print(closures)
                    for closure in closures:
                        content = closure.cell_contents
                        if isinstance(content, types.FunctionType):
                            necessary_params_count += \
                                BaseVerifier.check_instructions(content, prohibited_params=prohibited_params,
                                                                necessary_params=necessary_params)
                else:
                    if isinstance(value, types.FunctionType):
                        necessary_params_count += \
                            BaseVerifier.check_instructions(value, prohibited_params=prohibited_params,
                                                            necessary_params=necessary_params)
            except AttributeError:
                pass

        # print(necessary_params_count)
        if necessary_params_count < len(necessary_params):
            raise TypeError(
                f"Ошибка инициализации параметров {necessary_params}\n"
                f"Метод\\Атрибут(ы) отсутствуют")

    @staticmethod
    @log_exception(Exception)
    def check_instructions(
            content,
            prohibited_params: list = None,
            necessary_params: list = None):
        instr = dis.get_instructions(content)

        params = set()
        necessary_params_count = 0
        for i in instr:
            if i.opname == "LOAD_GLOBAL":
                params.add(i.argval)

            elif i.opname == "LOAD_ATTR":
                params.add(i.argval)

        if prohibited_params is not None:
            for param in params:
                if param in prohibited_params:
                    raise TypeError(
                        f"Ошибка инициализации параметра {param}\n"
                        f"Метод\\Атрибут запрещен для использования")

        if necessary_params is not None:
            for param in necessary_params:
                if param in params:
                    necessary_params_count += 1

        # print(params)

        return necessary_params_count


class ServerVerifier(BaseVerifier):
    """Server metaclass"""
    def __init__(cls, name, bases, attr):
        prohibited_params = ["connect"]
        necessary_params = ["AF_INET", "SOCK_STREAM"]
        cls.start_verify(attr, prohibited_params, necessary_params)

        super(ServerVerifier, cls).__init__(name, bases, attr)


class ClientVerifier(BaseVerifier):
    """Client metaclass"""
    def __init__(cls, name, bases, attr):
        prohibited_params = ["socket", "accept", "listen"]
        necessary_params = ["send_request", "get_answer"]
        cls.start_verify(attr, prohibited_params, necessary_params)

        super(ClientVerifier, cls).__init__(name, bases, attr)
