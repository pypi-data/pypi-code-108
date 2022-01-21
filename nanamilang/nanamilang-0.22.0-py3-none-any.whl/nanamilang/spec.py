"""NanamiLang Spec Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import (
    ASSERT_COLL_LENGTH_IS_EVEN,
    ASSERT_COLL_CONTAINS_ELEMENT,
    ASSERT_COLLECTION_IS_NOT_EMPTY,
    ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF,
)


class Spec:
    """NanamiLang Spec"""
    ArityIs: str = 'ArityIs'
    ArityEven: str = 'ArityEven'
    ArityVariants: str = 'ArityVariants'
    ArityAtLeastOne: str = 'ArityAtLeastOne'
    EachArgumentTypeIs: str = 'EachArgumentTypeIs'
    EachArgumentTypeVariants: str = 'EachArgumentTypeVariants'
    ArgumentsTypeChainVariants: str = 'ArgumentsTypeChainVariants'

    @staticmethod
    def validate(label: str, collection: tuple, flags: list):
        """NanamiLang Spec.validate() function implementation"""

        for maybe_flag_pair in flags:
            if len(maybe_flag_pair) == 2:
                flag, v = maybe_flag_pair
            else:
                flag, v = maybe_flag_pair[0], None
            if flag == Spec.ArityAtLeastOne:
                ASSERT_COLLECTION_IS_NOT_EMPTY(
                    collection,
                    f'{label}: '
                    f'invalid arity, at least one form/argument expected')
            elif flag == Spec.ArityIs:
                assert len(collection) == v, (
                    f'{label}: invalid arity, form(s)/argument(s) possible: {v}'
                )
            elif flag == Spec.ArityEven:
                ASSERT_COLL_LENGTH_IS_EVEN(
                    collection,
                    f'{label}: invalid arity, number of form(s)/argument(s) must be even')
            elif flag == Spec.ArityVariants:
                ASSERT_COLL_CONTAINS_ELEMENT(
                    len(collection),
                    v,
                    f'{label}: invalid arity, form(s)/argument(s) possible: {", ".join(map(str, v))}')
            elif flag == Spec.EachArgumentTypeIs:
                ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
                    collection,
                    v, f'{label}: can only accept {v.name} argument(s)')
            elif flag == Spec.EachArgumentTypeVariants:
                assert len(tuple(filter(lambda x: issubclass(x.__class__, v),
                                        collection))) == len(collection), (
                    f'{label}: can only accept {" or ".join([possible.name for possible in v])} arg(s)')
            elif flag == Spec.ArgumentsTypeChainVariants:
                if collection:
                    for possible in v:
                        if len(tuple(filter(lambda p: issubclass(collection[p[0]].__class__, (p[1],)),
                                            enumerate(possible)))) == len(collection):
                            return
                    raise AssertionError(f'{label}: the function arguments type chain was not appropriate')
