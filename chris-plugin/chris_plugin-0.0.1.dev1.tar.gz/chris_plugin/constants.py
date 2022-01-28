from chris_plugin.types import ParameterType
import logging


class Placeholders:
    """
    The ChRIS store requires a default value to be provided for
    arguments which are optional, however argparse doesn't care.
    If the ChRIS plugin does not specify a default for an argument
    that is optional, we will add these placeholders when serializing the parameters.

    https://github.com/FNNDSC/ChRIS_store/blob/0295268f7cd65593a259a7a00b83eac8ae876c33/store_backend/plugins/serializers.py#L404-L407
    """
    INT = -1
    FLOAT = 0.0
    STR = ''
    BOOL = False

    _logger = logging.getLogger(__name__)

    @classmethod
    def get_for(cls, t: ParameterType) -> int | float | str | bool:
        cls.__check_not(t, 'path')
        cls.__check_not(t, 'unextpath')
        cls._logger.warning('optional parameter does not specify a default')
        return cls.__dict__[t.upper()]

    @staticmethod
    def __check_not(t: ParameterType, s: str):
        if t == s:
            raise ValueError(f'parameter with {t} type may not be optional')
