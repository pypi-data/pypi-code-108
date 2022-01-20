import pathlib
import typing
import zipfile

import momotor.bundles
from momotor.bundles.base import Bundle
from momotor.bundles.binding import Results as ResultsRootType
from momotor.bundles.const import BundleCategory
from momotor.bundles.elements.result import create_error_result, Result
from momotor.bundles.elements.results import Results, ResultsBase

__all__ = ['ResultsBundle', 'create_error_result_bundle']


BT = typing.TypeVar("BT", bound=Bundle)


class ResultsBundle(Bundle[ResultsRootType], ResultsBase[ResultsRootType]):
    """ A results bundle. This implements the interface to create and access Momotor result files
    """
    def __init__(self, base: typing.Union[str, pathlib.Path] = None, zip_file: zipfile.ZipFile = None):
        Bundle.__init__(self, base, zip_file)
        Results.__init__(self, self)

    # noinspection PyShadowingBuiltins
    def create(self: BT, *,
               id: str = None,
               results: typing.Iterable[Result] = None) -> BT:
        """ Set all attributes for this ResultsBundle

        Usage:

        .. code-block:: python

           results = ResultsBundle(...).create(id, results)

        :param id: `id` of the bundle (optional)
        :param results: sequence of results (optional)
        :return: self
        """
        Results.create(self, id=id, results=results)
        return self

    def recreate(self, target_bundle: "momotor.bundles.Bundle") -> typing.NoReturn:
        """ not implemented """
        raise NotImplementedError

    @staticmethod
    def get_node_type() -> typing.Type[ResultsRootType]:
        return ResultsRootType

    @staticmethod
    def get_default_xml_name():
        """ Get the default XML file name

        :return: 'result.xml'
        """
        return 'result.xml'

    @staticmethod
    def get_category():
        """ Get the category for this bundle

        :return: :py:const:`BundleCategory.RESULTS`
        """
        return BundleCategory.RESULTS


def create_error_result_bundle(result_id: str, status: str, report: str = None, **properties) -> ResultsBundle:
    """ Helper to create an error result bundle with a single step with an error

    :param result_id: `id` of the step
    :param status: error status of the step
    :param report: error report of the step
    :param properties: additional properties to add
    :return: A :py:class:`~momotor.bundles.ResultsBundle` with the error step
    """
    bundle = ResultsBundle()
    bundle.create(results=[
        create_error_result(bundle, result_id, status, report, **properties)
    ])
    return bundle


# Extend the docstring with the generic documentation of Bundle
if ResultsBundle.__doc__ and Bundle.__doc__:
    ResultsBundle.__doc__ += "\n".join(Bundle.__doc__.split("\n")[1:])
