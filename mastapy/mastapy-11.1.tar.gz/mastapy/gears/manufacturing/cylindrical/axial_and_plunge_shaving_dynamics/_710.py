'''_710.py

AxialShaverRedressing
'''


from mastapy.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import _724, _711
from mastapy._internal.python_net import python_net_import

_AXIAL_SHAVER_REDRESSING = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics', 'AxialShaverRedressing')


__docformat__ = 'restructuredtext en'
__all__ = ('AxialShaverRedressing',)


class AxialShaverRedressing(_724.ShaverRedressing['_711.ConventionalShavingDynamics']):
    '''AxialShaverRedressing

    This is a mastapy class.
    '''

    TYPE = _AXIAL_SHAVER_REDRESSING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AxialShaverRedressing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
