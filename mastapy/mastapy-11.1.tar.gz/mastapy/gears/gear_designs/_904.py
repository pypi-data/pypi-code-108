'''_904.py

GearDesign
'''


from mastapy._internal import constructor
from mastapy.gears.fe_model import _1144
from mastapy.gears.fe_model.cylindrical import _1148
from mastapy._internal.cast_exception import CastException
from mastapy.gears.fe_model.conical import _1151
from mastapy.gears.gear_designs import _905
from mastapy._internal.python_net import python_net_import

_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns', 'GearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('GearDesign',)


class GearDesign(_905.GearDesignComponent):
    '''GearDesign

    This is a mastapy class.
    '''

    TYPE = _GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def number_of_teeth(self) -> 'int':
        '''int: 'NumberOfTeeth' is the original name of this property.'''

        return self.wrapped.NumberOfTeeth

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'int'):
        self.wrapped.NumberOfTeeth = int(value) if value else 0

    @property
    def number_of_teeth_maintaining_ratio(self) -> 'int':
        '''int: 'NumberOfTeethMaintainingRatio' is the original name of this property.'''

        return self.wrapped.NumberOfTeethMaintainingRatio

    @number_of_teeth_maintaining_ratio.setter
    def number_of_teeth_maintaining_ratio(self, value: 'int'):
        self.wrapped.NumberOfTeethMaintainingRatio = int(value) if value else 0

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def shaft_inner_diameter(self) -> 'float':
        '''float: 'ShaftInnerDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftInnerDiameter

    @property
    def absolute_shaft_inner_diameter(self) -> 'float':
        '''float: 'AbsoluteShaftInnerDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteShaftInnerDiameter

    @property
    def shaft_outer_diameter(self) -> 'float':
        '''float: 'ShaftOuterDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftOuterDiameter

    @property
    def names_of_meshing_gears(self) -> 'str':
        '''str: 'NamesOfMeshingGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NamesOfMeshingGears

    @property
    def mass(self) -> 'float':
        '''float: 'Mass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Mass

    @property
    def tifffe_model(self) -> '_1144.GearFEModel':
        '''GearFEModel: 'TIFFFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1144.GearFEModel.TYPE not in self.wrapped.TIFFFEModel.__class__.__mro__:
            raise CastException('Failed to cast tifffe_model to GearFEModel. Expected: {}.'.format(self.wrapped.TIFFFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TIFFFEModel.__class__)(self.wrapped.TIFFFEModel) if self.wrapped.TIFFFEModel is not None else None

    @property
    def tifffe_model_of_type_cylindrical_gear_fe_model(self) -> '_1148.CylindricalGearFEModel':
        '''CylindricalGearFEModel: 'TIFFFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1148.CylindricalGearFEModel.TYPE not in self.wrapped.TIFFFEModel.__class__.__mro__:
            raise CastException('Failed to cast tifffe_model to CylindricalGearFEModel. Expected: {}.'.format(self.wrapped.TIFFFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TIFFFEModel.__class__)(self.wrapped.TIFFFEModel) if self.wrapped.TIFFFEModel is not None else None

    @property
    def tifffe_model_of_type_conical_gear_fe_model(self) -> '_1151.ConicalGearFEModel':
        '''ConicalGearFEModel: 'TIFFFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1151.ConicalGearFEModel.TYPE not in self.wrapped.TIFFFEModel.__class__.__mro__:
            raise CastException('Failed to cast tifffe_model to ConicalGearFEModel. Expected: {}.'.format(self.wrapped.TIFFFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TIFFFEModel.__class__)(self.wrapped.TIFFFEModel) if self.wrapped.TIFFFEModel is not None else None
