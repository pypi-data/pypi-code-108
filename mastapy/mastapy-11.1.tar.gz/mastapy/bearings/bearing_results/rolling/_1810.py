'''_1810.py

MaximumStaticContactStress
'''


from mastapy.bearings.bearing_results.rolling import _1812
from mastapy._internal.python_net import python_net_import

_MAXIMUM_STATIC_CONTACT_STRESS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'MaximumStaticContactStress')


__docformat__ = 'restructuredtext en'
__all__ = ('MaximumStaticContactStress',)


class MaximumStaticContactStress(_1812.MaximumStaticContactStressResultsAbstract):
    '''MaximumStaticContactStress

    This is a mastapy class.
    '''

    TYPE = _MAXIMUM_STATIC_CONTACT_STRESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MaximumStaticContactStress.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
