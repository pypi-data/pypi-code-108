'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._1243 import AssemblyMethods
    from ._1244 import CalculationMethods
    from ._1245 import InterferenceFitDesign
    from ._1246 import InterferenceFitHalfDesign
    from ._1247 import StressRegions
    from ._1248 import Table4JointInterfaceTypes
