'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._918 import StraightBevelDiffGearDesign
    from ._919 import StraightBevelDiffGearMeshDesign
    from ._920 import StraightBevelDiffGearSetDesign
    from ._921 import StraightBevelDiffMeshedGearDesign
