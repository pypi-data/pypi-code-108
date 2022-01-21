'''_7027.py

ContactChartPerToothPass
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONTACT_CHART_PER_TOOTH_PASS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'ContactChartPerToothPass')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactChartPerToothPass',)


class ContactChartPerToothPass(_0.APIBase):
    '''ContactChartPerToothPass

    This is a mastapy class.
    '''

    TYPE = _CONTACT_CHART_PER_TOOTH_PASS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ContactChartPerToothPass.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def max_pressure(self) -> 'Image':
        '''Image: 'MaxPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.MaxPressure)
        return value

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
