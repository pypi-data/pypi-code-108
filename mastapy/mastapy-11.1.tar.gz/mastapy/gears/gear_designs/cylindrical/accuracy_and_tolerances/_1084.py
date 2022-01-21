'''_1084.py

AGMAISO13282013AccuracyGrader
'''


from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import _1089
from mastapy._internal.python_net import python_net_import

_AGMAISO13282013_ACCURACY_GRADER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances', 'AGMAISO13282013AccuracyGrader')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAISO13282013AccuracyGrader',)


class AGMAISO13282013AccuracyGrader(_1089.ISO13282013AccuracyGrader):
    '''AGMAISO13282013AccuracyGrader

    This is a mastapy class.
    '''

    TYPE = _AGMAISO13282013_ACCURACY_GRADER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAISO13282013AccuracyGrader.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
