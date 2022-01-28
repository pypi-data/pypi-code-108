import os
from typing import Literal, TypedDict, Optional, Any


ChrisPluginType = Literal['fs', 'ds', 'ts']
ParameterType = Literal['str', 'float', 'int', 'bool', 'path', 'unextpath']
"""
https://github.com/FNNDSC/ChRIS_store/blob/8f4fc98b3d87dc9aa3f7fbb314684021680a5945/store_backend/plugins/models.py#L12-L18
"""


class Special:
    """
    Types specific to ChRIS. These cannot be used outside the context of ChRIS,
    i.e. they cannot be used for true command-line apps.
    """
    @staticmethod
    def unextpath(_s: str) -> str:
        """
        Define the 'unextpath' data type that can be used by apps.
        It's a string representing a list of paths separated by commas. Unlike the
        'path' data type this type means that files won't be extracted from object
        storage.
        """
        path_list = [s.strip() for s in _s.split(',')]
        return ','.join(path_list)

    @staticmethod
    def path(_s: str) -> str:
        """
        Define the 'path' data type that can be used by apps.
        It's a string representing a list of paths separated by commas.
        """

        # https://github.com/FNNDSC/chrisapp/blob/fa9b0a68b78a4feeee2c96c61fbe04f5f296f301/chrisapp/base.py#L285-L295
        path_list = [s.strip() for s in _s.split(',')]
        for path in path_list:
            if not os.path.exists(path):
                raise ValueError(f'Path {path} not found!')
        return ','.join(path_list)


class ParameterSpec(TypedDict):
    """
    A description of a ChRIS plugin parameter as spec-ed by the ChRIS store.
    """
    name: str
    type: ParameterType
    optional: bool
    flag: str
    short_flag: str
    action: str
    help: str
    default: Optional[Any]
    ui_exposed: bool
