import collections.abc
import pathlib
import typing
import zipfile
from pathlib import PurePosixPath

import momotor.bundles
from momotor.bundles.base import Bundle
from momotor.bundles.binding import Testresult as TestresultRootType, ResultsComplexType
from momotor.bundles.const import BundleCategory
from momotor.bundles.elements.results import Results
from momotor.bundles.utils.assertion import assert_elements_instanceof
from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments
from momotor.bundles.utils.immutable import ImmutableOrderedDict


__all__ = ['TestResultBundle']


BT = typing.TypeVar("BT", bound=Bundle)


class TestResultBundle(Bundle[TestresultRootType]):
    """ A test results bundle. This implements the interface to create and access Momotor result files containing
    test results
    """

    __test__ = False  # Prevent pytest from using this as a test case

    __unset: typing.ClassVar = object()
    _results: ImmutableOrderedDict[str, Results] = __unset

    def __init__(self, base: typing.Union[str, pathlib.Path] = None, zip_file: zipfile.ZipFile = None):
        Bundle.__init__(self, base, zip_file)

    @property
    def results(self) -> typing.List[Results]:
        """ `results` children """
        assert self._results is not self.__unset, "Uninitialized attribute `results`"
        return list(self._results.values())

    @results.setter
    def results(self, results: typing.Iterable[Results]):
        assert self._results is self.__unset, "Immutable attribute `results`"
        assert isinstance(results, collections.abc.Iterable), "Invalid type for attribute `results`"

        self._results = assert_elements_instanceof(
            ImmutableOrderedDict(
                (results_bundle.id, results_bundle)
                for results_bundle in results
            ), Results, self
        )

    def create(self: BT, *, results: typing.Iterable[Results] = None) -> BT:
        """ Set all attributes for this TestResultBundle

        Usage:

        .. code-block:: python

           test_result = TestResultBundle(...).create(results)

        :param results: list of results (optional)
        :return: self
        """
        self.results = results
        return self

    def recreate(self, target_bundle: "momotor.bundles.Bundle", ) -> typing.NoReturn:
        raise NotImplementedError

    # noinspection PyMethodOverriding,PyProtectedMember
    def _create_from_node(self: BT, node: TestresultRootType, *, args: BundleFactoryArguments) -> BT:
        self._check_node_type(node)

        return self.create(
            results=(
                Results(self)._create_from_node(results, node, args=args) for results in node.results
            ) if node.results else None
        )

    def _construct_node(self, *, args: BundleConstructionArguments) -> TestresultRootType:
        return TestresultRootType(
            results=list(self._construct_results_nodes(args=args))
        )

    def _construct_results_nodes(self, *, args: BundleConstructionArguments) \
            -> typing.Generator[ResultsComplexType, None, None]:
        results = self.results
        if results:
            for result in results:
                # noinspection PyProtectedMember
                yield result._construct_node(args=args)

    @staticmethod
    def get_node_type() -> typing.Type[TestresultRootType]:
        return TestresultRootType

    @staticmethod
    def get_default_xml_name():
        """ Get the default XML file name

        :return: 'result.xml'
        """
        return 'result.xml'

    @staticmethod
    def get_category():
        """ Get the category for this bundle

        :return: :py:const:`BundleCategory.TEST_RESULTS`
        """
        return BundleCategory.TEST_RESULTS


# Extend the docstring with the generic documentation of Bundle
if TestResultBundle.__doc__ and Bundle.__doc__:
    TestResultBundle.__doc__ += "\n".join(Bundle.__doc__.split("\n")[1:])
