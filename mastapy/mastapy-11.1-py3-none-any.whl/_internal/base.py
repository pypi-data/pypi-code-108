'''base.py

This is a collection of empty base classes that get inserted by
_DummyBaseClassImporter to prevent errors when modifying __bases__.
'''


from typing import Generic, TypeVar


T = TypeVar('T')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')
T5 = TypeVar('T5')
T6 = TypeVar('T6')
T7 = TypeVar('T7')


class Base:
    '''Base

    Base class used by the dummy base class importer.
    '''


class GenericBase(Base, Generic[T]):
    '''GenericBase

    Generic Base class used by the dummy base class importer.
    '''


class GenericBase2(Base, Generic[T, T2]):
    '''GenericBase2

    Generic Base class with 2 generic parameters used by the
    dummy base class importer.
    '''


class GenericBase3(Base, Generic[T, T2, T3]):
    '''GenericBase3

    Generic Base class with 3 generic parameters used by the
    dummy base class importer.
    '''


class GenericBase4(Base, Generic[T, T2, T3, T4]):
    '''GenericBase4

    Generic Base class with 4 generic parameters used by the
    dummy base class importer.
    '''


class GenericBase5(Base, Generic[T, T2, T3, T4, T5]):
    '''GenericBase5

    Generic Base class with 5 generic parameters used by the
    dummy base class importer.
    '''


class GenericBase6(Base, Generic[T, T2, T3, T4, T5, T6]):
    '''GenericBase6

    Generic Base class with 6 generic parameters used by the
    dummy base class importer.
    '''


class GenericBase7(Base, Generic[T, T2, T3, T4, T5, T6, T7]):
    '''GenericBase7

    Generic Base class with 7 generic parameters used by the
    dummy base class importer.
    '''
