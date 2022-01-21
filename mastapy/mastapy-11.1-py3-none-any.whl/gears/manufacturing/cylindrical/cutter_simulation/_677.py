'''_677.py

ShaperSimulationCalculator
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.cutters.tangibles import _704
from mastapy.gears.manufacturing.cylindrical.cutter_simulation import _663
from mastapy._internal.python_net import python_net_import

_SHAPER_SIMULATION_CALCULATOR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'ShaperSimulationCalculator')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaperSimulationCalculator',)


class ShaperSimulationCalculator(_663.CutterSimulationCalc):
    '''ShaperSimulationCalculator

    This is a mastapy class.
    '''

    TYPE = _SHAPER_SIMULATION_CALCULATOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaperSimulationCalculator.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cutting_pressure_angle(self) -> 'float':
        '''float: 'CuttingPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CuttingPressureAngle

    @property
    def cutting_centre_distance(self) -> 'float':
        '''float: 'CuttingCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CuttingCentreDistance

    @property
    def shaper_sap_diameter(self) -> 'float':
        '''float: 'ShaperSAPDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaperSAPDiameter

    @property
    def shaper(self) -> '_704.CylindricalGearShaperTangible':
        '''CylindricalGearShaperTangible: 'Shaper' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_704.CylindricalGearShaperTangible)(self.wrapped.Shaper) if self.wrapped.Shaper is not None else None
