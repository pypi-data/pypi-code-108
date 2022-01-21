'''_934.py

KlingelnbergCycloPalloidHypoidGearDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.klingelnberg_conical import _938
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergHypoid', 'KlingelnbergCycloPalloidHypoidGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearDesign',)


class KlingelnbergCycloPalloidHypoidGearDesign(_938.KlingelnbergConicalGearDesign):
    '''KlingelnbergCycloPalloidHypoidGearDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pitch_diameter(self) -> 'float':
        '''float: 'PitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDiameter

    @property
    def mean_pitch_diameter(self) -> 'float':
        '''float: 'MeanPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanPitchDiameter

    @property
    def mean_spiral_angle(self) -> 'float':
        '''float: 'MeanSpiralAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanSpiralAngle

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def outer_tip_diameter(self) -> 'float':
        '''float: 'OuterTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterTipDiameter

    @property
    def inner_tip_diameter(self) -> 'float':
        '''float: 'InnerTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerTipDiameter

    @property
    def pitch_depth(self) -> 'float':
        '''float: 'PitchDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDepth

    @property
    def outer_root_diameter(self) -> 'float':
        '''float: 'OuterRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterRootDiameter

    @property
    def inner_root_diameter(self) -> 'float':
        '''float: 'InnerRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerRootDiameter
