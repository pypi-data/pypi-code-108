'''_636.py

HobManufactureError
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _649
from mastapy._internal.python_net import python_net_import

_HOB_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'HobManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('HobManufactureError',)


class HobManufactureError(_649.RackManufactureError):
    '''HobManufactureError

    This is a mastapy class.
    '''

    TYPE = _HOB_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HobManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_sin_curve_for_top_relief(self) -> 'bool':
        '''bool: 'UseSinCurveForTopRelief' is the original name of this property.'''

        return self.wrapped.UseSinCurveForTopRelief

    @use_sin_curve_for_top_relief.setter
    def use_sin_curve_for_top_relief(self, value: 'bool'):
        self.wrapped.UseSinCurveForTopRelief = bool(value) if value else False

    @property
    def total_relief_variation(self) -> 'float':
        '''float: 'TotalReliefVariation' is the original name of this property.'''

        return self.wrapped.TotalReliefVariation

    @total_relief_variation.setter
    def total_relief_variation(self, value: 'float'):
        self.wrapped.TotalReliefVariation = float(value) if value else 0.0
