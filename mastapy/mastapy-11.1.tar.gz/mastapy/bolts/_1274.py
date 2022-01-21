'''_1274.py

ClampedSectionMaterialDatabase
'''


from mastapy.bolts import _1265, _1264
from mastapy._internal.python_net import python_net_import

_CLAMPED_SECTION_MATERIAL_DATABASE = python_net_import('SMT.MastaAPI.Bolts', 'ClampedSectionMaterialDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('ClampedSectionMaterialDatabase',)


class ClampedSectionMaterialDatabase(_1265.BoltedJointMaterialDatabase['_1264.BoltedJointMaterial']):
    '''ClampedSectionMaterialDatabase

    This is a mastapy class.
    '''

    TYPE = _CLAMPED_SECTION_MATERIAL_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClampedSectionMaterialDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
