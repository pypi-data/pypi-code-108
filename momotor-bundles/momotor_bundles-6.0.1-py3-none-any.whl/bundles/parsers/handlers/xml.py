import typing

from xsdata.exceptions import XmlHandlerError
from xsdata.formats.dataclass.parsers.handlers import XmlSaxHandler


class XmlBundleEventHandler(XmlSaxHandler):
    def parse(self, source: typing.Any) -> typing.Any:
        if getattr(self.parser.config, 'process_xslt', None):
            raise XmlHandlerError(
                f"{type(self).__name__} doesn't support xslt transformation."
            )

        if getattr(self.parser.config, 'validation_schema_path', None):
            raise XmlHandlerError(
                f"{type(self).__name__} doesn't support validation."
            )

        return super().parse(source)
