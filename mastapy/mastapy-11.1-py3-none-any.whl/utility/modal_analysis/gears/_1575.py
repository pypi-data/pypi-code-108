'''_1575.py

OrderWithRadius
'''


from mastapy._internal import constructor
from mastapy.utility.modal_analysis.gears import _1573
from mastapy._internal.python_net import python_net_import

_ORDER_WITH_RADIUS = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis.Gears', 'OrderWithRadius')


__docformat__ = 'restructuredtext en'
__all__ = ('OrderWithRadius',)


class OrderWithRadius(_1573.OrderForTE):
    '''OrderWithRadius

    This is a mastapy class.
    '''

    TYPE = _ORDER_WITH_RADIUS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OrderWithRadius.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0
