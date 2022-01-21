'''_732.py

AbstractTCA
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical import _1107
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_TCA = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'AbstractTCA')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractTCA',)


class AbstractTCA(_0.APIBase):
    '''AbstractTCA

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_TCA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractTCA.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def peak_to_peak_transmission_error_with_respect_to_wheel(self) -> 'float':
        '''float: 'PeakToPeakTransmissionErrorWithRespectToWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeakToPeakTransmissionErrorWithRespectToWheel

    @property
    def mean_transmission_error_with_respect_to_wheel(self) -> 'float':
        '''float: 'MeanTransmissionErrorWithRespectToWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanTransmissionErrorWithRespectToWheel

    @property
    def conical_mesh_misalignments(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'ConicalMeshMisalignments' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.ConicalMeshMisalignments) if self.wrapped.ConicalMeshMisalignments is not None else None
