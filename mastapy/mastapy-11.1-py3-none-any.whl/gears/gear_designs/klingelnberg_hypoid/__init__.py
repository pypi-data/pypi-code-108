'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._934 import KlingelnbergCycloPalloidHypoidGearDesign
    from ._935 import KlingelnbergCycloPalloidHypoidGearMeshDesign
    from ._936 import KlingelnbergCycloPalloidHypoidGearSetDesign
    from ._937 import KlingelnbergCycloPalloidHypoidMeshedGearDesign
