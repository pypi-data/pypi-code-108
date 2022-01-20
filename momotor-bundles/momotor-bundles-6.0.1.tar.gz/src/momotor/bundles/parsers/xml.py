import typing
from dataclasses import dataclass

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.bases import Parsed
from xsdata.formats.dataclass.parsers.mixins import XmlNode


@dataclass
class XmlBundleParser(XmlParser):
    """ Extends :py:class:`~xsdata.formats.dataclass.parsers.XmlParser` with validation of the bundle type
    by checking that the root node tag is as expected
    """
    expected_root_qname: str = None

    def start(
        self,
        clazz: typing.Type,
        queue: typing.List[XmlNode],
        objects: typing.List[Parsed],
        qname: str,
        attrs: typing.Dict,
        ns_map: typing.Dict,
    ):
        if len(queue) == 0 and qname != self.expected_root_qname:
            from momotor.bundles import InvalidBundle
            raise InvalidBundle(f'Unexpected node {qname}, expected {self.expected_root_qname}')

        super().start(clazz, queue, objects, qname, attrs, ns_map)
