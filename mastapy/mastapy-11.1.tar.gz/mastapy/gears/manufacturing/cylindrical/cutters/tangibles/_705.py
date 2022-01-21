'''_705.py

CylindricalGearShaverTangible
'''


from mastapy.gears.manufacturing.cylindrical.cutters import _693, _688
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.cutters.tangibles import _701
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SHAVER_TANGIBLE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters.Tangibles', 'CylindricalGearShaverTangible')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearShaverTangible',)


class CylindricalGearShaverTangible(_701.CutterShapeDefinition):
    '''CylindricalGearShaverTangible

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SHAVER_TANGIBLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearShaverTangible.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def design(self) -> '_693.CylindricalGearShaver':
        '''CylindricalGearShaver: 'Design' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _693.CylindricalGearShaver.TYPE not in self.wrapped.Design.__class__.__mro__:
            raise CastException('Failed to cast design to CylindricalGearShaver. Expected: {}.'.format(self.wrapped.Design.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Design.__class__)(self.wrapped.Design) if self.wrapped.Design is not None else None
