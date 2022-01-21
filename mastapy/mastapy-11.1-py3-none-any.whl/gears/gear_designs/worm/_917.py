'''_917.py

WormWheelDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.worm import _914
from mastapy._internal.python_net import python_net_import

_WORM_WHEEL_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Worm', 'WormWheelDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('WormWheelDesign',)


class WormWheelDesign(_914.WormGearDesign):
    '''WormWheelDesign

    This is a mastapy class.
    '''

    TYPE = _WORM_WHEEL_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormWheelDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def addendum(self) -> 'float':
        '''float: 'Addendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Addendum

    @property
    def dedendum(self) -> 'float':
        '''float: 'Dedendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Dedendum

    @property
    def reference_diameter(self) -> 'float':
        '''float: 'ReferenceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceDiameter

    @property
    def reference_helix_angle(self) -> 'float':
        '''float: 'ReferenceHelixAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceHelixAngle

    @property
    def mean_helix_angle(self) -> 'float':
        '''float: 'MeanHelixAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanHelixAngle

    @property
    def mean_diameter(self) -> 'float':
        '''float: 'MeanDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanDiameter

    @property
    def throat_tip_diameter(self) -> 'float':
        '''float: 'ThroatTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThroatTipDiameter

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterDiameter

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidth

    @property
    def throat_radius(self) -> 'float':
        '''float: 'ThroatRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThroatRadius

    @property
    def working_pitch_diameter(self) -> 'float':
        '''float: 'WorkingPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingPitchDiameter

    @property
    def whole_depth(self) -> 'float':
        '''float: 'WholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WholeDepth

    @property
    def root_diameter(self) -> 'float':
        '''float: 'RootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootDiameter
