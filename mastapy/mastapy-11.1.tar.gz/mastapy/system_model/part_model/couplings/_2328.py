'''_2328.py

PartToPartShearCoupling
'''


from mastapy.system_model.connections_and_sockets.couplings import _2090
from mastapy._internal import constructor
from mastapy.system_model.part_model.couplings import _2323
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'PartToPartShearCoupling')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCoupling',)


class PartToPartShearCoupling(_2323.Coupling):
    '''PartToPartShearCoupling

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCoupling.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def part_to_part_shear_coupling_connection(self) -> '_2090.PartToPartShearCouplingConnection':
        '''PartToPartShearCouplingConnection: 'PartToPartShearCouplingConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2090.PartToPartShearCouplingConnection)(self.wrapped.PartToPartShearCouplingConnection) if self.wrapped.PartToPartShearCouplingConnection is not None else None
