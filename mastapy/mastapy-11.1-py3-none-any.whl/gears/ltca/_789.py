'''_789.py

CylindricalGearFilletNodeStressResultsColumn
'''


from mastapy._internal import constructor
from mastapy.gears.ltca import _798
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FILLET_NODE_STRESS_RESULTS_COLUMN = python_net_import('SMT.MastaAPI.Gears.LTCA', 'CylindricalGearFilletNodeStressResultsColumn')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFilletNodeStressResultsColumn',)


class CylindricalGearFilletNodeStressResultsColumn(_798.GearFilletNodeStressResultsColumn):
    '''CylindricalGearFilletNodeStressResultsColumn

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FILLET_NODE_STRESS_RESULTS_COLUMN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFilletNodeStressResultsColumn.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width_position(self) -> 'float':
        '''float: 'FaceWidthPosition' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthPosition
