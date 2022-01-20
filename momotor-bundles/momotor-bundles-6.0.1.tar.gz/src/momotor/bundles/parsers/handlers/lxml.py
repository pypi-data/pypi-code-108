import typing
from functools import lru_cache

try:
    from lxml import etree
    from xsdata.formats.dataclass.parsers.handlers.lxml import LxmlEventHandler, EVENTS

except ImportError:
    LxmlBundleEventHandler = None

else:
    from .exceptions import ValidationError


    @lru_cache(maxsize=16)
    def _get_schema(path: str) -> etree.XMLSchema:
        with open(path) as schema_file:
            return etree.XMLSchema(file=schema_file)

    class LxmlBundleEventHandler(LxmlEventHandler):
        """ Extends :py:class:`~xsdata.formats.dataclass.parsers.handlers.LxmlEventHandler`
        to add support for large documents and XSLT
        """
        def parse(self, source: typing.Any) -> typing.Any:
            """
            Parse an XML document from a system identifier or an InputSource.

            The xml parser will ignore comments, recover from errors. The
            parser will parse the whole document and then walk down the tree
            if the process xinclude is enabled.
            """
            lxml_parser = etree.XMLParser(
                huge_tree=getattr(self.parser.config, 'huge_tree', True),
                recover=True,
                remove_comments=True,
            )

            tree = etree.parse(
                source,
                parser=lxml_parser,
                base_url=self.parser.config.base_url
            )

            if getattr(self.parser.config, 'process_xslt', True):
                stylesheet = tree.xpath('//processing-instruction("xml-stylesheet")')
                if stylesheet:
                    xsl = stylesheet[0].parseXSL()
                    xsl.xinclude()
                    tree = tree.xslt(xsl)

            if self.parser.config.process_xinclude:
                tree.xinclude()

            validation_schema_path = getattr(self.parser.config, 'validation_schema_path', True)
            if validation_schema_path:
                schema = _get_schema(str(validation_schema_path))
                try:
                    schema.assertValid(tree)
                except etree.DocumentInvalid as e:
                    raise ValidationError(str(e))

            ctx = etree.iterwalk(tree, EVENTS)

            return self.process_context(ctx)
