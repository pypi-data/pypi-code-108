'''_1151.py

ConicalGearFEModel
'''


from mastapy.gears.fe_model import _1144
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_FE_MODEL = python_net_import('SMT.MastaAPI.Gears.FEModel.Conical', 'ConicalGearFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearFEModel',)


class ConicalGearFEModel(_1144.GearFEModel):
    '''ConicalGearFEModel

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearFEModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
