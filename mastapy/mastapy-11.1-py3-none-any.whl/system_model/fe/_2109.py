'''_2109.py

ContactPairWithSelection
'''


from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import _176
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONTACT_PAIR_WITH_SELECTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'ContactPairWithSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactPairWithSelection',)


class ContactPairWithSelection(_0.APIBase):
    '''ContactPairWithSelection

    This is a mastapy class.
    '''

    TYPE = _CONTACT_PAIR_WITH_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ContactPairWithSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_pair(self) -> '_176.ContactPairReporting':
        '''ContactPairReporting: 'ContactPair' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_176.ContactPairReporting)(self.wrapped.ContactPair) if self.wrapped.ContactPair is not None else None

    def select_reference_surface(self):
        ''' 'SelectReferenceSurface' is the original name of this method.'''

        self.wrapped.SelectReferenceSurface()

    def select_constrained_surface(self):
        ''' 'SelectConstrainedSurface' is the original name of this method.'''

        self.wrapped.SelectConstrainedSurface()

    def select_contacting_reference_surface(self):
        ''' 'SelectContactingReferenceSurface' is the original name of this method.'''

        self.wrapped.SelectContactingReferenceSurface()

    def select_contacting_constrained_surface(self):
        ''' 'SelectContactingConstrainedSurface' is the original name of this method.'''

        self.wrapped.SelectContactingConstrainedSurface()
