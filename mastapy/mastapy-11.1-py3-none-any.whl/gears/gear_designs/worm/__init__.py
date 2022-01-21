'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._913 import WormDesign
    from ._914 import WormGearDesign
    from ._915 import WormGearMeshDesign
    from ._916 import WormGearSetDesign
    from ._917 import WormWheelDesign
