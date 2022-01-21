'''_1985.py

AdvancedSystemDeflectionViewable
'''


from mastapy.system_model.drawing import _1984
from mastapy._internal.python_net import python_net_import

_ADVANCED_SYSTEM_DEFLECTION_VIEWABLE = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'AdvancedSystemDeflectionViewable')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedSystemDeflectionViewable',)


class AdvancedSystemDeflectionViewable(_1984.AbstractSystemDeflectionViewable):
    '''AdvancedSystemDeflectionViewable

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_SYSTEM_DEFLECTION_VIEWABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedSystemDeflectionViewable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
