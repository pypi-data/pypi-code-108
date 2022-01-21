'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._1513 import ScriptingSetup
    from ._1514 import UserDefinedPropertyKey
    from ._1515 import UserSpecifiedData
