'''_1308.py

EulerParameters
'''


from mastapy.math_utility import _1324
from mastapy._internal.python_net import python_net_import

_EULER_PARAMETERS = python_net_import('SMT.MastaAPI.MathUtility', 'EulerParameters')


__docformat__ = 'restructuredtext en'
__all__ = ('EulerParameters',)


class EulerParameters(_1324.RealVector):
    '''EulerParameters

    This is a mastapy class.
    '''

    TYPE = _EULER_PARAMETERS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EulerParameters.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
