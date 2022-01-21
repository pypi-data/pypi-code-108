'''_1001.py

FinishToothThicknessDesignSpecification
'''


from mastapy.gears.gear_designs.cylindrical import _1040
from mastapy._internal.python_net import python_net_import

_FINISH_TOOTH_THICKNESS_DESIGN_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'FinishToothThicknessDesignSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('FinishToothThicknessDesignSpecification',)


class FinishToothThicknessDesignSpecification(_1040.ToothThicknessSpecificationBase):
    '''FinishToothThicknessDesignSpecification

    This is a mastapy class.
    '''

    TYPE = _FINISH_TOOTH_THICKNESS_DESIGN_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FinishToothThicknessDesignSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
