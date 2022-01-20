import collections.abc
import typing
from pathlib import PurePosixPath

import momotor.bundles
from momotor.bundles.base import Bundle
from momotor.bundles.binding import Recipe as RecipeRootType, StepsComplexType, StepComplexType
from momotor.bundles.const import BundleCategory
from momotor.bundles.elements.files import FilesMixin, File
from momotor.bundles.mixins.id import IdMixin
from momotor.bundles.elements.options import Option, OptionsMixin
from momotor.bundles.elements.steps import Step
from momotor.bundles.utils.assertion import assert_element_mapping_instanceof
from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments
from momotor.bundles.utils.keyedtuple import KeyedTuple
from momotor.bundles.utils.nodes import get_nested_complex_nodes

__all__ = ['RecipeBundle']


BT = typing.TypeVar("BT")


StepsType = typing.Union[KeyedTuple[Step], typing.Mapping[str, Step], typing.Iterable[Step]]


class StepKeyedTuple(KeyedTuple[Step]):
    """ The results as a :py:class:`~momotor.bundles.utils.keyedsequence.KeyedTuple`
    of :py:class:`~momotor.bundles.elements.result.Result` objects.

    The KeyedTuple allows access as a tuple or a mapping. Results are indexed by their `step_id` attribute
    """

    def __init__(self, steps: StepsType = None):
        super().__init__(steps, key_attr='id')


class RecipeBundle(Bundle[RecipeRootType], IdMixin, OptionsMixin, FilesMixin):
    """ A recipe bundle. This implements the interface to create and access Momotor recipe files
    """
    __unset: typing.ClassVar = object()

    _steps: KeyedTuple[Step] = __unset

    @property
    def steps(self) -> KeyedTuple[Step]:
        """ The recipe's `steps` """
        assert self._steps is not self.__unset, "Uninitialized attribute `steps`"
        return self._steps

    @steps.setter
    def steps(self, steps: StepsType):
        assert self._steps is self.__unset, "Immutable attribute `steps`"
        assert isinstance(steps, (KeyedTuple, collections.abc.Mapping, collections.abc.Iterable))
        self._steps = assert_element_mapping_instanceof(StepKeyedTuple(steps), str, Step, self)

    @property
    def tests(self) -> KeyedTuple:
        """ The recipe's `tests` (not implemented yet) """
        return KeyedTuple()

    @tests.setter
    def tests(self, tests: typing.Optional[typing.Iterable]):
        pass

    # noinspection PyShadowingBuiltins
    def create(self: BT, *,
               id: str = None,
               options: typing.Iterable[Option] = None,
               files: typing.Iterable[File] = None,
               steps: typing.Iterable[Step],
               tests: typing.Iterable = None) -> BT:
        """ Set all attributes for this RecipeBundle

        Usage:

        .. code-block:: python

           recipe = RecipeBundle(...).create(id, options, steps, tests)

        :param id: `id` of the bundle (optional)
        :param options: list of options (optional)
        :param files: list of files (optional)
        :param steps: list of steps
        :param tests: list of tests (optional)
        :return: self
        """
        self.id = id
        self.options = options
        self.files = files
        self.steps = steps
        self.tests = tests
        return self

    def recreate(self, target_bundle: "momotor.bundles.Bundle") -> typing.NoReturn:
        """ not implemented """
        raise NotImplementedError

    def _create_from_node(self: BT, node: RecipeRootType, *, args: BundleFactoryArguments) -> BT:
        self._check_node_type(node)

        return self.create(
            id=node.id,
            options=self._collect_options(node, [], args=args),
            files=self._collect_files(node, [], args=args),
            steps=self._collect_steps(node, args=args),
            tests=self._collect_tests(node, args=args),
        )

    def _collect_steps(self, node: RecipeRootType, *, args: BundleFactoryArguments) -> typing.Generator[Step, None, None]:
        steps_node: typing.Optional[StepsComplexType] = None
        for tag_name, child_node in get_nested_complex_nodes(node, 'steps', 'step'):
            if tag_name == 'steps':
                steps_node = typing.cast(StepsComplexType, child_node)
            else:
                step_node = typing.cast(StepComplexType, child_node)
                # noinspection PyProtectedMember
                yield Step(self)._create_from_node(step_node, steps_node, node, args=args)

    # noinspection PyMethodMayBeStatic
    def _collect_tests(self, node: RecipeRootType, *, args: BundleFactoryArguments):  # TODO
        return None

    # noinspection PyProtectedMember
    def _construct_node(self, *, args: BundleConstructionArguments) -> RecipeRootType:
        return RecipeRootType(
            id=self.id,
            options=list(self._construct_options_nodes(args=args)),
            files=list(self._construct_files_nodes(args=args)),
            steps=list(self._construct_steps_nodes(args=args)),
            # tests=list(self._construct_tests_nodes(args=args)),
        )

    def _construct_steps_nodes(self, *, args: BundleConstructionArguments) -> typing.Generator[StepsComplexType, None, None]:
        assert self._steps is not self.__unset, "Uninitialized attribute `steps`"

        if self._steps:
            # noinspection PyProtectedMember
            yield StepsComplexType(step=[
                step._construct_node(args=args) for step in self._steps.values()
            ])

    @staticmethod
    def get_node_type() -> typing.Type[RecipeRootType]:
        return RecipeRootType

    @staticmethod
    def get_default_xml_name():
        """ Get the default XML file name

        :return: 'recipe.xml'
        """
        return 'recipe.xml'

    @staticmethod
    def get_category():
        """ Get the category for this bundle

        :return: :py:const:`BundleCategory.RECIPE`
        """
        return BundleCategory.RECIPE


# Extend the docstring with the generic documentation of Bundle
if RecipeBundle.__doc__ and Bundle.__doc__:
    RecipeBundle.__doc__ += "\n".join(Bundle.__doc__.split("\n")[1:])
