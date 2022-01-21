'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._942 import HypoidGearDesign
    from ._943 import HypoidGearMeshDesign
    from ._944 import HypoidGearSetDesign
    from ._945 import HypoidMeshedGearDesign
