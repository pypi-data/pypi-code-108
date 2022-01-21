'''_6652.py

PlanetarySocketManufactureError
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6654
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLANETARY_SOCKET_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PlanetarySocketManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetarySocketManufactureError',)


class PlanetarySocketManufactureError(_0.APIBase):
    '''PlanetarySocketManufactureError

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_SOCKET_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetarySocketManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def socket_name(self) -> 'str':
        '''str: 'SocketName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SocketName

    @property
    def planet_manufacture_errors(self) -> 'List[_6654.PlanetManufactureError]':
        '''List[PlanetManufactureError]: 'PlanetManufactureErrors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetManufactureErrors, constructor.new(_6654.PlanetManufactureError))
        return value
