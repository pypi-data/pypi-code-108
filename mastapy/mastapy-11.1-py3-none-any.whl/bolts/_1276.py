'''_1276.py

DetailedBoltedJointDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.bolts import _1280
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DETAILED_BOLTED_JOINT_DESIGN = python_net_import('SMT.MastaAPI.Bolts', 'DetailedBoltedJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('DetailedBoltedJointDesign',)


class DetailedBoltedJointDesign(_0.APIBase):
    '''DetailedBoltedJointDesign

    This is a mastapy class.
    '''

    TYPE = _DETAILED_BOLTED_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DetailedBoltedJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_bolts(self) -> 'int':
        '''int: 'NumberOfBolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfBolts

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def loaded_bolts(self) -> 'List[_1280.LoadedBolt]':
        '''List[LoadedBolt]: 'LoadedBolts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadedBolts, constructor.new(_1280.LoadedBolt))
        return value
