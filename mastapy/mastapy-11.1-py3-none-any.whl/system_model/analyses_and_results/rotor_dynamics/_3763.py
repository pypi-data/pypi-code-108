'''_3763.py

ShaftModalComplexShapeAtSpeeds
'''


from mastapy.system_model.analyses_and_results.rotor_dynamics import _3762
from mastapy._internal.python_net import python_net_import

_SHAFT_MODAL_COMPLEX_SHAPE_AT_SPEEDS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.RotorDynamics', 'ShaftModalComplexShapeAtSpeeds')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftModalComplexShapeAtSpeeds',)


class ShaftModalComplexShapeAtSpeeds(_3762.ShaftModalComplexShape):
    '''ShaftModalComplexShapeAtSpeeds

    This is a mastapy class.
    '''

    TYPE = _SHAFT_MODAL_COMPLEX_SHAPE_AT_SPEEDS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftModalComplexShapeAtSpeeds.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
