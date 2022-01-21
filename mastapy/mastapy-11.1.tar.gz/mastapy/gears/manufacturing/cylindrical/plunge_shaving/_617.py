'''_617.py

VirtualPlungeShaverOutputs
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.gears.manufacturing.cylindrical.cutters import _693, _688
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.plunge_shaving import _611
from mastapy._internal.python_net import python_net_import

_VIRTUAL_PLUNGE_SHAVER_OUTPUTS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'VirtualPlungeShaverOutputs')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualPlungeShaverOutputs',)


class VirtualPlungeShaverOutputs(_611.PlungeShaverOutputs):
    '''VirtualPlungeShaverOutputs

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_PLUNGE_SHAVER_OUTPUTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualPlungeShaverOutputs.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def lead_modification_on_conjugate_shaver_chart_left_flank(self) -> 'Image':
        '''Image: 'LeadModificationOnConjugateShaverChartLeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.LeadModificationOnConjugateShaverChartLeftFlank)
        return value

    @property
    def lead_modification_on_conjugate_shaver_chart_right_flank(self) -> 'Image':
        '''Image: 'LeadModificationOnConjugateShaverChartRightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.LeadModificationOnConjugateShaverChartRightFlank)
        return value

    @property
    def shaver(self) -> '_693.CylindricalGearShaver':
        '''CylindricalGearShaver: 'Shaver' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _693.CylindricalGearShaver.TYPE not in self.wrapped.Shaver.__class__.__mro__:
            raise CastException('Failed to cast shaver to CylindricalGearShaver. Expected: {}.'.format(self.wrapped.Shaver.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Shaver.__class__)(self.wrapped.Shaver) if self.wrapped.Shaver is not None else None
