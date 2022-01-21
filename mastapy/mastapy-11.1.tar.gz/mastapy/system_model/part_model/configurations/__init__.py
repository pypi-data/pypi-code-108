'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._2351 import ActiveFESubstructureSelection
    from ._2352 import ActiveFESubstructureSelectionGroup
    from ._2353 import ActiveShaftDesignSelection
    from ._2354 import ActiveShaftDesignSelectionGroup
    from ._2355 import BearingDetailConfiguration
    from ._2356 import BearingDetailSelection
    from ._2357 import PartDetailConfiguration
    from ._2358 import PartDetailSelection
