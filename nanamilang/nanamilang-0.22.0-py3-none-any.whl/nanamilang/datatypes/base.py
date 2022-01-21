"""NanamiLang Base Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import \
    ASSERT_DICT_CONTAINS_KEY, \
    ASSERT_COLLECTION_IS_NOT_EMPTY, \
    ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF, \
    ASSERT_IS_INSTANCE_OF, ASSERT_COLL_LENGTH_IS_EVEN


class Base:
    """NanamiLang Base Data Type Class"""

    _hashed: int
    name: str = 'Base'
    _expected_type = None
    _python_reference = None

    def __init__(self, reference) -> None:
        """NanamiLang Base Data Type, initialize new instance"""

        ASSERT_IS_INSTANCE_OF(
            reference,
            self._expected_type,
            message=f'{self.name}: {self._expected_type} expected'
        )

        self._set_hash(reference)

        self._additional_assertions_on_init(reference)

        self._python_reference = reference

    def nominal(self) -> 'Base':
        """NanamiLang Bse Data Type, nominal() virtual"""

        raise NotImplementedError

    def _set_hash(self, reference) -> None:
        """NanamiLang Base Data Type, default implementation"""

        self._hashed = hash(reference)

    def _additional_assertions_on_init(self,
                                       reference) -> None:
        """NanamiLang Base Data Type, default implementation"""

        # By default, there are no additional assertions to run

    def hashed(self) -> int:
        """NanamiLang Base Data Type, default implementation"""

        return self._hashed

    def truthy(self) -> bool:
        """NanamiLang Base Data Type, default implementation"""

        # If not overridden in derived class
        # let Python3 make a right choice about reference truthy
        return bool(self.reference())  # by casting it to a bool

    def init_assert_reference_has_keys(self,
                                       reference,
                                       keys: tuple) -> None:
        """NanamiLang Base Data Type, does reference has keys"""

        for key in keys:
            ASSERT_DICT_CONTAINS_KEY(
                key, reference,
                f'{self.name}: "ref" has no needed "{key}" key'
            )

    def _init_assert_ref_could_not_be_empty(self,
                                            reference) -> None:
        """NanamiLang Base Data Type, ref could not be empty"""

        ASSERT_COLLECTION_IS_NOT_EMPTY(
            reference, f'{self.name}: "ref" could not be empty')

    def _init_assert_ref_length_must_be_even(self,
                                             reference) -> None:
        """NanamiLang Base Data Type, ref length must be even"""

        ASSERT_COLL_LENGTH_IS_EVEN(
            reference, f'{self.name}: "ref" length must be even')

    def _init_assert_only_base(self, reference) -> None:
        """NanamiLang Base Data Type, assert that only base types"""

        ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
            reference,
            Base,
            f'{self.name}: can only host/contain NanamiLang types')

    def reference(self):
        """NanamiLang Base Data Type, self._python_reference getter"""

        return self._python_reference

    def origin(self) -> str:
        """NanamiLang Base Data Type, children may have this method"""

        # But default implementation is to return a Python 3 NoneType.

    def format(self, **_) -> str:
        """NanamiLang Base Data Type, format() default implementation"""

        return f'{self._python_reference}'  # <- cast any type to string

    def __str__(self) -> str:
        """NanamiLang Base Data Type, __str__() method implementation"""

        return f'<{self.name}>: {self.format()}'  # <- i.e.: <Base>: foo

    def __repr__(self) -> str:
        """NanamiLang Base Data Type, __repr__() method implementation"""

        return self.__str__()  # <- use defined self.__str__() meth above
