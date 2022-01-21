'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._938 import KlingelnbergConicalGearDesign
    from ._939 import KlingelnbergConicalGearMeshDesign
    from ._940 import KlingelnbergConicalGearSetDesign
    from ._941 import KlingelnbergConicalMeshedGearDesign
