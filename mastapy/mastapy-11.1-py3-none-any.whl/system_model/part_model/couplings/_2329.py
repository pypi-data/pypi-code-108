'''_2329.py

PartToPartShearCouplingHalf
'''


from mastapy.system_model.part_model.couplings import _2324
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'PartToPartShearCouplingHalf')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingHalf',)


class PartToPartShearCouplingHalf(_2324.CouplingHalf):
    '''PartToPartShearCouplingHalf

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_HALF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingHalf.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
