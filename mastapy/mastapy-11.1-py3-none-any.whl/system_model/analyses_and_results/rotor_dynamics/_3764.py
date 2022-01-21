'''_3764.py

ShaftModalComplexShapeAtStiffness
'''


from mastapy.system_model.analyses_and_results.rotor_dynamics import _3762
from mastapy._internal.python_net import python_net_import

_SHAFT_MODAL_COMPLEX_SHAPE_AT_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.RotorDynamics', 'ShaftModalComplexShapeAtStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftModalComplexShapeAtStiffness',)


class ShaftModalComplexShapeAtStiffness(_3762.ShaftModalComplexShape):
    '''ShaftModalComplexShapeAtStiffness

    This is a mastapy class.
    '''

    TYPE = _SHAFT_MODAL_COMPLEX_SHAPE_AT_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftModalComplexShapeAtStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
