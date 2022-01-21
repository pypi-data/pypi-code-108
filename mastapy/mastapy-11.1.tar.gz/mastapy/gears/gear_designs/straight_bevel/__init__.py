'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._922 import StraightBevelGearDesign
    from ._923 import StraightBevelGearMeshDesign
    from ._924 import StraightBevelGearSetDesign
    from ._925 import StraightBevelMeshedGearDesign
