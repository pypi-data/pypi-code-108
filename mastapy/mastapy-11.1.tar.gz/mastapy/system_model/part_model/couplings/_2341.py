'''_2341.py

SpringDamperHalf
'''


from mastapy.system_model.part_model.couplings import _2324
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SpringDamperHalf')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalf',)


class SpringDamperHalf(_2324.CouplingHalf):
    '''SpringDamperHalf

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalf.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
