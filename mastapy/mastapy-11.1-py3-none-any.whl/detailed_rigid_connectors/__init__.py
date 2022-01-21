'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._1187 import DetailedRigidConnectorDesign
    from ._1188 import DetailedRigidConnectorHalfDesign
