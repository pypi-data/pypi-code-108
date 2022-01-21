'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._2084 import ClutchConnection
    from ._2085 import ClutchSocket
    from ._2086 import ConceptCouplingConnection
    from ._2087 import ConceptCouplingSocket
    from ._2088 import CouplingConnection
    from ._2089 import CouplingSocket
    from ._2090 import PartToPartShearCouplingConnection
    from ._2091 import PartToPartShearCouplingSocket
    from ._2092 import SpringDamperConnection
    from ._2093 import SpringDamperSocket
    from ._2094 import TorqueConverterConnection
    from ._2095 import TorqueConverterPumpSocket
    from ._2096 import TorqueConverterTurbineSocket
