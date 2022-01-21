'''_6536.py

BeltDriveLoadCase
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.part_model.couplings import _2316, _2326
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.static_loads import _6670
from mastapy._internal.python_net import python_net_import

_BELT_DRIVE_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'BeltDriveLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('BeltDriveLoadCase',)


class BeltDriveLoadCase(_6670.SpecialisedAssemblyLoadCase):
    '''BeltDriveLoadCase

    This is a mastapy class.
    '''

    TYPE = _BELT_DRIVE_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BeltDriveLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pre_tension(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PreTension' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PreTension) if self.wrapped.PreTension is not None else None

    @pre_tension.setter
    def pre_tension(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PreTension = value

    @property
    def assembly_design(self) -> '_2316.BeltDrive':
        '''BeltDrive: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2316.BeltDrive.TYPE not in self.wrapped.AssemblyDesign.__class__.__mro__:
            raise CastException('Failed to cast assembly_design to BeltDrive. Expected: {}.'.format(self.wrapped.AssemblyDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyDesign.__class__)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None
