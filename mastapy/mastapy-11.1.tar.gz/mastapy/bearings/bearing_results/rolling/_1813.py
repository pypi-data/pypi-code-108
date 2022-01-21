'''_1813.py

MaxStripLoadStressObject
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MAX_STRIP_LOAD_STRESS_OBJECT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'MaxStripLoadStressObject')


__docformat__ = 'restructuredtext en'
__all__ = ('MaxStripLoadStressObject',)


class MaxStripLoadStressObject(_0.APIBase):
    '''MaxStripLoadStressObject

    This is a mastapy class.
    '''

    TYPE = _MAX_STRIP_LOAD_STRESS_OBJECT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MaxStripLoadStressObject.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_strip_load(self) -> 'float':
        '''float: 'MaximumStripLoad' is the original name of this property.'''

        return self.wrapped.MaximumStripLoad

    @maximum_strip_load.setter
    def maximum_strip_load(self, value: 'float'):
        self.wrapped.MaximumStripLoad = float(value) if value else 0.0
