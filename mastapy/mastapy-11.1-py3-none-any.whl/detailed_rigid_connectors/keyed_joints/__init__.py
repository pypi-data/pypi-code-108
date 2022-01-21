'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._1237 import KeyedJointDesign
    from ._1238 import KeyTypes
    from ._1239 import KeywayJointHalfDesign
    from ._1240 import NumberOfKeys
