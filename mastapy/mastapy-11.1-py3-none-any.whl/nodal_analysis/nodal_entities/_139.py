'''_139.py

PIDControlNodalComponent
'''


from mastapy.nodal_analysis.nodal_entities import _136
from mastapy._internal.python_net import python_net_import

_PID_CONTROL_NODAL_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'PIDControlNodalComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('PIDControlNodalComponent',)


class PIDControlNodalComponent(_136.NodalComponent):
    '''PIDControlNodalComponent

    This is a mastapy class.
    '''

    TYPE = _PID_CONTROL_NODAL_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PIDControlNodalComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
