from io import BytesIO

import pathlib
import typing
import zipfile

from .lxml import use_lxml


__all__ = ['detect_bundle_type']


if typing.TYPE_CHECKING:
    from momotor.bundles import Bundle
    from .arguments import BundleFactoryArguments


def detect_bundle_type(path_or_data: typing.Union[pathlib.Path, bytes, memoryview],
                       args: "BundleFactoryArguments") -> typing.Type["Bundle"]:
    """ Implementation of :py:meth:`momotor.bundles.Bundle.detect`.

    Use that, instead of this function.
    """
    from momotor.bundles import RecipeBundle, ConfigBundle, ProductBundle, ResultsBundle, TestResultBundle
    from momotor.bundles.exception import InvalidBundle

    bundle_types = [
        RecipeBundle, ConfigBundle, ProductBundle, ResultsBundle, TestResultBundle
    ]

    bundle_by_tag = {
        bundle_type.get_root_qname(): bundle_type
        for bundle_type in bundle_types
    }

    if use_lxml(args.use_lxml):
        from lxml import etree  # noqa
        parser = etree.XMLParser(huge_tree=True, recover=True, remove_comments=True)

        def _get_root_tag(content: typing.IO) -> typing.Optional[str]:
            try:
                tree = etree.parse(content, parser=parser)

                stylesheet = tree.xpath('//processing-instruction("xml-stylesheet")')
                if stylesheet:
                    xsl = stylesheet[0].parseXSL()
                    xsl.xinclude()
                    tree = tree.xslt(xsl)

                tree.xinclude()

                return tree.getroot().tag
            except:  # noqa
                return None

    else:
        from xml.etree import ElementTree

        def _get_root_tag(content: typing.IO) -> typing.Optional[str]:
            try:
                return ElementTree.parse(content).getroot().tag
            except:  # noqa
                return None

    def _default_xml_name(typ: typing.Type["Bundle"]) -> str:
        return args.xml_name or typ.get_default_xml_name()

    is_data = isinstance(path_or_data, (bytes, memoryview))

    if zipfile.is_zipfile(BytesIO(path_or_data) if is_data else path_or_data):
        with zipfile.ZipFile(BytesIO(path_or_data) if is_data else path_or_data) as zf:
            # First, for all bundle types, check if the expected xml file exists
            for typ in bundle_types:
                try:
                    with zf.open(_default_xml_name(typ)) as xml_file:
                        if _get_root_tag(xml_file) == typ.get_root_qname():
                            return typ
                except KeyError:
                    pass

            # Otherwise, scan all xml files in the root of the zip to find a match
            for name in zf.namelist():
                if '/' not in name and name.endswith('.xml'):
                    with zf.open(name) as xml_file:
                        root_tag = _get_root_tag(xml_file)

                    try:
                        return bundle_by_tag[root_tag]
                    except KeyError:
                        pass

    elif is_data:
        try:
            return bundle_by_tag[_get_root_tag(BytesIO(path_or_data))]
        except KeyError:
            pass

    else:
        if not path_or_data.exists():
            raise FileNotFoundError

        elif path_or_data.is_dir():
            # First, for all bundle types, check if the expected xml file exists
            for typ in bundle_types:
                xml_path = path_or_data / _default_xml_name(typ)
                if xml_path.exists():
                    with xml_path.open() as xml_file:
                        if _get_root_tag(xml_file) == typ.get_root_qname():
                            return typ

            # Otherwise, scan all xml files in the directory to find a match
            for name in path_or_data.glob('*.xml'):
                xml_path = path_or_data / name
                with xml_path.open() as xml_file:
                    root_tag = _get_root_tag(xml_file)

                try:
                    return bundle_by_tag[root_tag]
                except KeyError:
                    pass

        else:
            with path_or_data.open() as xml_file:
                try:
                    return bundle_by_tag[_get_root_tag(xml_file)]
                except KeyError:
                    pass

    raise InvalidBundle
