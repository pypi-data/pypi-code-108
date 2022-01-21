'''__init__.py'''


from mastapy._internal.dummy_base_class_importer import _DummyBaseClassImport


with _DummyBaseClassImport():
    from ._1233 import AGMA6123SplineJointDutyCycleRating
    from ._1234 import GBT17855SplineJointDutyCycleRating
    from ._1235 import SAESplineJointDutyCycleRating
