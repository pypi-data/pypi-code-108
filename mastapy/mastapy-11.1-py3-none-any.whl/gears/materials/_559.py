'''_559.py

ISOTR1417912001CoefficientOfFrictionConstantsDatabase
'''


from mastapy.utility.databases import _1596
from mastapy.gears.materials import _558
from mastapy._internal.python_net import python_net_import

_ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS_DATABASE = python_net_import('SMT.MastaAPI.Gears.Materials', 'ISOTR1417912001CoefficientOfFrictionConstantsDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ISOTR1417912001CoefficientOfFrictionConstantsDatabase',)


class ISOTR1417912001CoefficientOfFrictionConstantsDatabase(_1596.NamedDatabase['_558.ISOTR1417912001CoefficientOfFrictionConstants']):
    '''ISOTR1417912001CoefficientOfFrictionConstantsDatabase

    This is a mastapy class.
    '''

    TYPE = _ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISOTR1417912001CoefficientOfFrictionConstantsDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
