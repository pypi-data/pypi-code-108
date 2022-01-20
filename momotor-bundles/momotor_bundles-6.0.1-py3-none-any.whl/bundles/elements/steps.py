import typing
import warnings
from enum import IntEnum
from pathlib import PurePosixPath

import momotor.bundles
from momotor.bundles.binding import DependsComplexType, StepComplexType, DependenciesComplexType, \
    StepsComplexType, RecipeComplexType, StepComplexTypePriority, CheckletComplexType
from momotor.bundles.elements.base import Element, NestedElement
from momotor.bundles.elements.checklets import Checklet, CheckletMixin
from momotor.bundles.elements.files import File, FilesMixin
from momotor.bundles.elements.options import Option, OptionsMixin
from momotor.bundles.elements.resources import ResourcesMixin, Resource, ResourcesType
from momotor.bundles.mixins.id import IdMixin
from momotor.bundles.utils.assertion import assert_elements_instanceof
from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments
from momotor.bundles.utils.filters import FilterableTuple
from momotor.bundles.utils.nodes import get_nested_complex_nodes

try:
    from typing import final
except ImportError:
    from typing_extensions import final

__all__ = ['Priority', 'Depends', 'Step']

ET = typing.TypeVar("ET", bound=Element)


class Priority(IntEnum):
    """ An enum for the step priority """
    MUST_PASS = 0
    HIGH = 1
    NORMAL = 2
    DEFAULT = 2
    LOW = 3


# Map StepComplexTypePriority to Priority
PRIORITY_LEVEL_MAP: typing.Dict[StepComplexTypePriority, Priority] = {
    StepComplexTypePriority.MUST_PASS: Priority.MUST_PASS,
    StepComplexTypePriority.HIGH: Priority.HIGH,
    StepComplexTypePriority.DEFAULT: Priority.DEFAULT,
    StepComplexTypePriority.NORMAL: Priority.NORMAL,
    StepComplexTypePriority.LOW: Priority.LOW,
}


class Depends(Element[DependsComplexType]):
    # noinspection PyUnresolvedReferences
    """ A Depends element encapsulating :py:class:`~momotor.bundles.binding.momotor.DependsComplexType`
    """

    __unset: typing.ClassVar = object()
    _step: typing.Optional[str] = __unset

    @final
    @property
    def step(self) -> str:
        """ `step` attribute """
        assert self._step is not self.__unset, "Uninitialized attribute `step`"
        return self._step

    @step.setter
    def step(self, step: str):
        assert self._step is self.__unset, "Immutable attribute `step`"
        assert isinstance(step, str)
        self._step = step

    @staticmethod
    def get_node_type() -> typing.Type[DependsComplexType]:
        return DependsComplexType

    def create(self: ET, *, step: str) -> ET:
        self.step = step
        return self

    def recreate(self: ET, target_bundle: "momotor.bundles.Bundle") -> ET:
        return Depends(target_bundle).create(step=self.step)

    # noinspection PyMethodOverriding
    def _create_from_node(self: ET, node: DependsComplexType, *, args: BundleFactoryArguments) -> ET:
        self._check_node_type(node)

        return self.create(step=node.step)

    def _construct_node(self, *, args: BundleConstructionArguments) -> DependsComplexType:
        return DependsComplexType(step=self.step)


if Depends.__doc__ and Element.__doc__:
    Depends.__doc__ += "\n".join(Element.__doc__.split("\n")[1:])


class Step(
    NestedElement[StepComplexType, StepsComplexType],
    CheckletMixin[StepComplexType],
    IdMixin, OptionsMixin, FilesMixin, ResourcesMixin,
):
    """ A Step element encapsulating :py:class:`~momotor.bundles.binding.momotor.StepComplexType`
    """
    __unset: typing.ClassVar = object()
    _priority: typing.Optional[StepComplexTypePriority] = __unset
    _depends: typing.Optional[FilterableTuple[Depends]] = __unset
    _checklet: typing.Optional[Checklet] = __unset
    _merged_resources = None

    @final
    @property
    def priority(self) -> str:
        """ `priority` attribute """
        assert self._priority is not self.__unset, "Uninitialized attribute `priority`"
        return self._priority.value

    @priority.setter
    def priority(self, priority: str):
        assert self._priority is self.__unset, "Immutable attribute `priority`"
        assert isinstance(priority, str)

        try:
            priority_enum = StepComplexTypePriority(priority)
        except ValueError:
            warnings.warn(f"Invalid priority attribute value '{priority}' ignored (will use 'default")
            priority_enum = StepComplexTypePriority.DEFAULT

        self._priority = priority_enum

    @final
    @property
    def depends(self) -> typing.Optional[FilterableTuple[Depends]]:
        """ `depends` """
        assert self._depends is not self.__unset, "Uninitialized attribute `depends`"
        return self._depends

    @depends.setter
    def depends(self, depends: typing.Optional[typing.Iterable[Depends]]):
        assert self._depends is self.__unset, "Immutable attribute `depends`"
        if depends is not None:
            self._depends = assert_elements_instanceof(FilterableTuple(depends), Depends, self.bundle)
        else:
            self._depends = None

    @final
    @property
    def checklet(self) -> typing.Optional[Checklet]:
        """ `checklet` """
        assert self._checklet is not self.__unset, "Uninitialized attribute `checklet`"
        return self._checklet

    @checklet.setter
    def checklet(self, checklet: typing.Optional[Checklet]):
        assert self._checklet is self.__unset, "Immutable attribute `checklet`"
        assert checklet is None or (isinstance(checklet, Checklet) and checklet.bundle == self.bundle)
        self._checklet = checklet
        self._resources_updated()

    def _resources_updated(self):
        super()._resources_updated()
        self._merged_resources = None

    @staticmethod
    def get_node_type() -> typing.Type[StepComplexType]:
        return StepComplexType

    @staticmethod
    def _get_parent_type() -> typing.Type[StepsComplexType]:
        return StepsComplexType

    # noinspection PyShadowingBuiltins
    def create(self: ET, *,
               id: str,
               priority: str = 'default',
               depends: typing.Iterable[Depends] = None,
               checklet: Checklet = None,
               options: typing.Iterable[Option] = None,
               files: typing.Iterable[File] = None,
               resources: typing.Iterable[Resource] = None) -> ET:

        self.id = id
        self.priority = priority
        self.depends = depends
        self.checklet = checklet
        self.options = options
        self.files = files
        self.resources = resources
        return self

    def recreate(self, target_bundle: "momotor.bundles.Bundle") -> typing.NoReturn:
        """ not implemented """
        raise NotImplementedError

    # noinspection PyMethodOverriding
    def _create_from_node(self, node: StepComplexType, steps: StepsComplexType, recipe: RecipeComplexType, *,
                          args: BundleFactoryArguments) -> ET:
        # recipe > steps > step
        #
        # step has <files> children
        #  - file.ref can refer to file in recipe.files
        #
        # step has single <checklet> child
        #  - checklet.ref can refer to checklet in steps.checklets or recipe.checklets

        self._check_node_type(node)
        self._check_parent_type(steps)
        # self._check_node_type(recipe, RecipeComplexType)

        return self.create(
            id=node.id,
            priority=node.priority.value,
            depends=self._collect_depends(node, args=args),
            checklet=self._collect_checklet(node, [steps.checklets, recipe.checklets], args=args),
            options=self._collect_options(node, [steps.options, recipe.options], args=args),
            files=self._collect_files(node, [recipe.files], args=args),
            resources=self._collect_resources(node, args=args)
        )

    def _collect_depends(self, node: StepComplexType, *,
                         args: BundleFactoryArguments) -> typing.Generator[Depends, None, None]:
        for tag_name, child in get_nested_complex_nodes(node, 'dependencies', 'depends'):
            if tag_name == 'depends':
                # noinspection PyProtectedMember
                yield Depends(self.bundle)._create_from_node(node=typing.cast(DependsComplexType, child), args=args)

    def _construct_node(self, *, args: BundleConstructionArguments) -> StepComplexType:
        return StepComplexType(
            id=self.id,
            priority=self._priority,
            dependencies=list(self._construct_dependencies_nodes(args=args)),
            checklet=list(self._construct_checklet_nodes(args=args)),
            options=list(self._construct_options_nodes(args=args)),
            files=list(self._construct_files_nodes(PurePosixPath('step', self.id), args=args)),
            resources=list(self._construct_resources_nodes(args=args)),
        )

    def _construct_dependencies_nodes(self, *, args: BundleConstructionArguments) \
            -> typing.Generator[DependenciesComplexType, None, None]:
        depends = self.depends
        if depends:
            yield DependenciesComplexType(depends=[
                dep._construct_node(args=args)
                for dep in depends
            ])

    def _construct_checklet_nodes(self, *, args: BundleConstructionArguments) \
            -> typing.Generator[CheckletComplexType, None, None]:
        checklet = self.checklet
        if checklet:
            # noinspection PyProtectedMember
            yield self.checklet._construct_node(args=args)

    @property
    def priority_value(self) -> Priority:
        """ `priority` attribute as :py:class:`Priority` instance """
        return PRIORITY_LEVEL_MAP.get(self._priority)

    def get_dependencies_ids(self) -> typing.Generator[str, None, None]:
        """ ids of the dependencies """
        if self.depends:
            for depend in self.depends:
                yield depend.step

    def get_resources(self) -> typing.Dict[str, ResourcesType]:
        """ get all resources needed by this step """
        if self._merged_resources is None:
            merged_resources = self._get_resources().copy()
            if self.checklet:
                for name, resources in self.checklet.get_resources().items():
                    if name in merged_resources:
                        merged_resources[name] += resources
                    else:
                        merged_resources[name] = resources

            self._merged_resources = merged_resources

        return self._merged_resources


if Step.__doc__ and Element.__doc__:
    Step.__doc__ += "\n".join(Element.__doc__.split("\n")[1:])
