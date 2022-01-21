'''_913.py

WormDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _316
from mastapy.gears.gear_designs.worm import _914
from mastapy._internal.python_net import python_net_import

_WORM_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Worm', 'WormDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('WormDesign',)


class WormDesign(_914.WormGearDesign):
    '''WormDesign

    This is a mastapy class.
    '''

    TYPE = _WORM_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def reference_diameter(self) -> 'float':
        '''float: 'ReferenceDiameter' is the original name of this property.'''

        return self.wrapped.ReferenceDiameter

    @reference_diameter.setter
    def reference_diameter(self, value: 'float'):
        self.wrapped.ReferenceDiameter = float(value) if value else 0.0

    @property
    def diameter_factor(self) -> 'float':
        '''float: 'DiameterFactor' is the original name of this property.'''

        return self.wrapped.DiameterFactor

    @diameter_factor.setter
    def diameter_factor(self, value: 'float'):
        self.wrapped.DiameterFactor = float(value) if value else 0.0

    @property
    def worm_starts(self) -> 'int':
        '''int: 'WormStarts' is the original name of this property.'''

        return self.wrapped.WormStarts

    @worm_starts.setter
    def worm_starts(self, value: 'int'):
        self.wrapped.WormStarts = int(value) if value else 0

    @property
    def reference_lead_angle(self) -> 'float':
        '''float: 'ReferenceLeadAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceLeadAngle

    @property
    def axial_pitch(self) -> 'float':
        '''float: 'AxialPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialPitch

    @property
    def lead(self) -> 'float':
        '''float: 'Lead' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Lead

    @property
    def axial_thickness(self) -> 'float':
        '''float: 'AxialThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialThickness

    @property
    def normal_thickness(self) -> 'float':
        '''float: 'NormalThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThickness

    @property
    def working_pitch_diameter(self) -> 'float':
        '''float: 'WorkingPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingPitchDiameter

    @property
    def working_pitch_lead_angle(self) -> 'float':
        '''float: 'WorkingPitchLeadAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingPitchLeadAngle

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
    def clearance(self) -> 'float':
        '''float: 'Clearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Clearance

    @property
    def fillet_radius(self) -> 'float':
        '''float: 'FilletRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilletRadius

    @property
    def tip_diameter(self) -> 'float':
        '''float: 'TipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipDiameter

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidth

    @property
    def addendum_factor(self) -> '_316.WormAddendumFactor':
        '''WormAddendumFactor: 'AddendumFactor' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AddendumFactor)
        return constructor.new(_316.WormAddendumFactor)(value) if value is not None else None

    @addendum_factor.setter
    def addendum_factor(self, value: '_316.WormAddendumFactor'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AddendumFactor = value

    @property
    def working_depth_factor(self) -> 'float':
        '''float: 'WorkingDepthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingDepthFactor

    @property
    def clearance_factor(self) -> 'float':
        '''float: 'ClearanceFactor' is the original name of this property.'''

        return self.wrapped.ClearanceFactor

    @clearance_factor.setter
    def clearance_factor(self, value: 'float'):
        self.wrapped.ClearanceFactor = float(value) if value else 0.0

    @property
    def fillet_radius_factor(self) -> 'float':
        '''float: 'FilletRadiusFactor' is the original name of this property.'''

        return self.wrapped.FilletRadiusFactor

    @fillet_radius_factor.setter
    def fillet_radius_factor(self, value: 'float'):
        self.wrapped.FilletRadiusFactor = float(value) if value else 0.0
