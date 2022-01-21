'''_1269.py

BoltMaterialDatabase
'''


from mastapy.bolts import _1265, _1268
from mastapy._internal.python_net import python_net_import

_BOLT_MATERIAL_DATABASE = python_net_import('SMT.MastaAPI.Bolts', 'BoltMaterialDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltMaterialDatabase',)


class BoltMaterialDatabase(_1265.BoltedJointMaterialDatabase['_1268.BoltMaterial']):
    '''BoltMaterialDatabase

    This is a mastapy class.
    '''

    TYPE = _BOLT_MATERIAL_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltMaterialDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
