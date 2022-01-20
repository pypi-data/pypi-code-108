import typing
from pathlib import PurePosixPath

import momotor.bundles
from momotor.bundles.base import Bundle
from momotor.bundles.binding import Product as ProductRootType
from momotor.bundles.const import BundleCategory
from momotor.bundles.mixins.id import IdMixin
from momotor.bundles.elements.files import File, FilesMixin
from momotor.bundles.elements.options import Option, OptionsMixin
from momotor.bundles.elements.properties import Property, PropertiesMixin

__all__ = ['ProductBundle']

from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments

BT = typing.TypeVar("BT", bound=Bundle)


class ProductBundle(Bundle[ProductRootType], IdMixin, OptionsMixin, FilesMixin, PropertiesMixin):
    """ A product bundle. This implements the interface to create and access Momotor product files
    """
    # noinspection PyShadowingBuiltins
    def create(self: BT, *,
               id: str = None,
               options: typing.Iterable[Option] = None,
               files: typing.Iterable[File] = None,
               properties: typing.Iterable[Property] = None) -> BT:
        """ Set all attributes for this ProductBundle

        Usage:

        .. code-block:: python

           product = ProductBundle(...).create(id, options, files)

        :param id: `id` of the bundle (optional)
        :param options: list of options (optional)
        :param files: list of files (optional)
        :param properties: list of properties (optional)
        :return: self
        """
        # TODO meta
        self.id = id
        self.options = options
        self.files = files
        self.properties = properties
        return self

    def recreate(self, target_bundle: "momotor.bundles.Bundle") -> typing.NoReturn:
        """ not implemented """
        raise NotImplementedError

    # noinspection PyMethodOverriding
    def _create_from_node(self: BT, node: ProductRootType, *, args: BundleFactoryArguments) -> BT:
        self._check_node_type(node)

        return self.create(
            id=node.id,
            options=self._collect_options(node, [], args=args),
            files=self._collect_files(node, [], args=args),
            properties=self._collect_properties(node, args=args),
        )

    def _construct_node(self, *, args: BundleConstructionArguments) -> ProductRootType:
        return ProductRootType(
            id=self.id,
            options=list(self._construct_options_nodes(args=args)),
            files=list(self._construct_files_nodes(args=args)),
            properties=list(self._construct_properties_nodes(args=args)),
        )

    @staticmethod
    def get_node_type() -> typing.Type[ProductRootType]:
        return ProductRootType

    @staticmethod
    def get_default_xml_name():
        """ Get the default XML file name

        :return: 'product.xml'
        """
        return 'product.xml'

    @staticmethod
    def get_category():
        """ Get the category for this bundle

        :return: :py:const:`BundleCategory.PRODUCT`
        """
        return BundleCategory.PRODUCT


# Extend the docstring with the generic documentation of Bundle
if ProductBundle.__doc__ and Bundle.__doc__:
    ProductBundle.__doc__ += "\n".join(Bundle.__doc__.split("\n")[1:])
