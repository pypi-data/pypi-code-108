import collections.abc

import typing
from abc import ABC
from pathlib import PurePosixPath

import momotor.bundles
from momotor.bundles.binding import ResultsComplexType, TestResultComplexType, ResultComplexType
from momotor.bundles.elements.base import Element, NestedElement
from momotor.bundles.mixins.id import IdMixin
from momotor.bundles.elements.result import Result
from momotor.bundles.utils.assertion import assert_elements_instanceof
from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments
from momotor.bundles.utils.keyedtuple import KeyedTuple

try:
    from typing import final
except ImportError:
    from typing_extensions import final

__all__ = ['ResultsBase', 'Results', 'ResultKeyedTuple']

ET = typing.TypeVar("ET", bound=Element)
RT = typing.TypeVar("RT")


ResultsType = typing.Union[KeyedTuple[Result], typing.Mapping[str, Result], typing.Iterable[Result]]


class ResultKeyedTuple(KeyedTuple[Result]):
    """ The results as a :py:class:`~momotor.bundles.utils.keyedtuple.KeyedTuple`
    of :py:class:`~momotor.bundles.elements.result.Result` objects.

    The KeyedTuple allows access as a tuple or a mapping. Results are indexed by their `step_id` attribute
    """

    def __init__(self, results: ResultsType = None):
        super().__init__(results, key_attr='step_id')


# noinspection PyProtectedMember
class ResultsBase(typing.Generic[RT], NestedElement[ResultsComplexType, TestResultComplexType], IdMixin, ABC):
    # noinspection PyUnresolvedReferences
    __unset: typing.ClassVar = object()
    _results: ResultKeyedTuple = __unset

    @final
    @property
    def results(self) -> ResultKeyedTuple:
        """ `results` children """
        assert self._results is not self.__unset, "Uninitialized attribute `results`"
        return self._results

    @results.setter
    def results(self, results: typing.Optional[typing.Iterable[Result]]):
        assert self._results is self.__unset, "Immutable attribute `results`"
        if results is None:
            self._results = ResultKeyedTuple()
        else:
            assert isinstance(results, (KeyedTuple, collections.abc.Mapping, collections.abc.Iterable))
            self._results = assert_elements_instanceof(
                ResultKeyedTuple(results), Result, self.bundle
            )

    @staticmethod
    def _get_parent_type() -> typing.Type[TestResultComplexType]:
        return TestResultComplexType

    # noinspection PyShadowingBuiltins
    def create(self: ET, *, id: str = None, results: ResultsType = None) -> ET:
        # TODO: meta
        self.id = id
        self.results = results
        return self

    # noinspection PyMethodOverriding
    def _create_from_node(self: ET, node: ResultsComplexType, testresult: TestResultComplexType = None, *,
                          args: BundleFactoryArguments) -> ET:
        self._check_node_type(node)
        self._check_parent_type(testresult, True)

        return self.create(
            id=node.id,
            results=[
                Result(self.bundle)._create_from_node(result, node, args=args) for result in node.result
            ] if node.result else None
        )

    def _construct_node(self, *, args: BundleConstructionArguments) -> RT:
        # TODO meta, checklets
        return self.get_node_type()(
            id=self.id,
            result=list(self._construct_result_nodes(args=args)),
            meta=[],  # TODO
            checklets=[]  # TODO
        )

    def _construct_result_nodes(self, *, args: BundleConstructionArguments) \
            -> typing.Generator[ResultComplexType, None, None]:
        results = self.results
        if results:
            for result in results.values():
                yield result._construct_node(args=args)


class Results(ResultsBase[ResultsComplexType]):
    """ A Results element encapsulating :py:class:`~momotor.bundles.binding.momotor.ResultsComplexType`
    """

    @staticmethod
    def get_node_type() -> typing.Type[ResultsComplexType]:
        return ResultsComplexType

    def recreate(self, target_bundle: "momotor.bundles.Bundle") -> typing.NoReturn:
        """ not implemented """
        raise NotImplementedError


if Results.__doc__ and Element.__doc__:
    Results.__doc__ += "\n".join(Element.__doc__.split("\n")[1:])
