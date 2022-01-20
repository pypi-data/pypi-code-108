import typing

import momotor.bundles
from momotor.bundles.base import Bundle
from momotor.bundles.binding import Config as ConfigRootType
from momotor.bundles.const import BundleCategory
from momotor.bundles.elements.files import File, FilesMixin
from momotor.bundles.elements.options import Option, OptionsMixin
from momotor.bundles.mixins.id import IdMixin

__all__ = ['ConfigBundle']

from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments

BT = typing.TypeVar("BT", bound=Bundle)


class ConfigBundle(Bundle[ConfigRootType], IdMixin, OptionsMixin, FilesMixin):
    """ A config bundle. This implements the interface to create and access Momotor configuration files
    """
    # noinspection PyShadowingBuiltins
    def create(self: BT, *,
               id: str = None,
               options: typing.Iterable[Option] = None,
               files: typing.Iterable[File] = None) -> BT:
        """ Set all attributes for this ConfigBundle

        Usage:

        .. code-block:: python

           config = ConfigBundle(...).create(id, options, files)

        :param id: `id` of the bundle (optional)
        :param options: list of options (optional)
        :param files: list of files (optional)
        :return: self
        """
        # TODO meta
        self.id = id
        self.options = options
        self.files = files
        return self

    def recreate(self, target_bundle: "momotor.bundles.Bundle") -> typing.NoReturn:
        """ not implemented """
        raise NotImplementedError

    # noinspection PyMethodOverriding
    def _create_from_node(self: BT, node: ConfigRootType, *, args: BundleFactoryArguments) -> BT:
        self._check_node_type(node)

        return self.create(
            id=node.id,
            options=self._collect_options(node, [], args=args),
            files=self._collect_files(node, [], args=args)
        )

    def _construct_node(self, *, args: BundleConstructionArguments) -> ConfigRootType:
        return ConfigRootType(
            id=self.id,
            options=list(self._construct_options_nodes(args=args)),
            files=list(self._construct_files_nodes(args=args)),
        )

    @staticmethod
    def get_node_type() -> typing.Type[ConfigRootType]:
        return ConfigRootType

    @staticmethod
    def get_default_xml_name() -> str:
        """ Get the default XML file name

        :return: 'config.xml'
        """
        return 'config.xml'

    @staticmethod
    def get_category() -> BundleCategory:
        """ Get the category for this bundle

        :return: :py:const:`BundleCategory.CONFIG`
        """
        return BundleCategory.CONFIG


# Extend the docstring with the generic documentation of Bundle
if ConfigBundle.__doc__ and Bundle.__doc__:
    ConfigBundle.__doc__ += "\n".join(Bundle.__doc__.split("\n")[1:])
