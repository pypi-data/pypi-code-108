'''_1039.py

ToothThicknessSpecification
'''


from mastapy.gears.gear_designs.cylindrical import _1040
from mastapy._internal.python_net import python_net_import

_TOOTH_THICKNESS_SPECIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ToothThicknessSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothThicknessSpecification',)


class ToothThicknessSpecification(_1040.ToothThicknessSpecificationBase):
    '''ToothThicknessSpecification

    This is a mastapy class.
    '''

    TYPE = _TOOTH_THICKNESS_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothThicknessSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
