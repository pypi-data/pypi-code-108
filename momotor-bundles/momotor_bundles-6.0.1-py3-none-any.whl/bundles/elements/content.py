import typing
import warnings
from abc import ABC
from collections import deque
from decimal import Decimal
from io import BytesIO
from pathlib import PurePosixPath, Path, PurePath

from xsdata.formats.dataclass.models.generics import AnyElement
from xsdata.utils.namespaces import build_qname

from momotor.bundles.binding.momotor_1_0 import __NAMESPACE__
from momotor.bundles.elements.base import NestedElement, Element
from momotor.bundles.mixins.attachments import SrcAttachmentMixin, AttachmentSrc
from momotor.bundles.mixins.name import NameStrMixin, NamePathMixin
from momotor.bundles.utils.arguments import BundleConstructionArguments, BundleFactoryArguments
from momotor.bundles.utils.boolean import to_bool
from momotor.bundles.utils.encoding import decode_data, encode_data

try:
    from typing import final
except ImportError:
    from typing_extensions import final

__all__ = [
    'ContentBasicElement', 'ContentFullElement', 'ContentAttachmentElement',
    'NO_CONTENT',
    'NoContent', 'AttachmentContent',
]


def is_printable(s: str) -> bool:
    return all((32 <= ord(c) < 127 or ord(c) >= 160) for c in s)


VALUE_TYPE_MAP = {
    'string': str,
    'integer': int,
    'float': float,
    'boolean': to_bool,
}

ALTERNATE_VALUE_TYPES = {
    'int': 'integer',
    'bool': 'boolean',
}

ET = typing.TypeVar('ET', bound="Element")
PT = typing.TypeVar('PT', bound=object)
CT = typing.TypeVar('CT', bound=object)
PCT = typing.TypeVar('PCT', bound=object)

true_qname = build_qname(__NAMESPACE__, 'true')
false_qname = build_qname(__NAMESPACE__, 'false')
none_qname = build_qname(__NAMESPACE__, 'none')

NO_CONTENT = object()

ContentBasicProcessedType = typing.Union[str, bool, None]
ContentFullProcessedType = typing.Union[ContentBasicProcessedType, bytes, int, float, Decimal]
RawType = typing.Union[str, bool, None]


class NoContent(ValueError):
    pass


class AttachmentContent(ValueError):
    pass


class ContentElementBase(typing.Generic[CT, PCT, PT], NestedElement[CT, PCT], NameStrMixin, ABC):
    """ Base class for elements with content, either as a value attribute, child nodes or as an attachment.
    Handles 'name', 'src', 'type', 'value' and 'encoding' attributes and child node content.
    This unifies the handling of <option>, <property> and <file> nodes

    The subclasses ContentTypeElement and ContentSrcElement exist mainly to create the proper documentation of the
    properties and methods.

    'src', 'value' and child nodes with content are mutually exclusive.
    'type' has a double role: For nodes with a 'value' attribute it indicates the type (string, integer or float),
    for nodes with child content or src, it is the content mime type.
    'encoding' is only used with child content, it is either 'base64' or 'quopri'

    TODO: src removed
    """
    HAS_ENCODING: typing.ClassVar
    VALID_PROCESSED_TYPES: typing.ClassVar
    MAX_VALUE_LENGTH: typing.ClassVar = 1000

    # _src: typing.Optional[PurePosixPath] = None  # The src attribute
    _value: typing.Optional[str] = None  # The value attribute
    _encoding: typing.Optional[str] = None  # The encoding attribute
    _content_set: bool = False  # Content has been provided

    _type: typing.Optional[str] = None
    _type_set: bool = False

    # Raw content is the content as it appears in the XML document, a sequence of str, bool or None items.
    #
    # Processed content is the content converted and decoded using the `type` and `encoding` attributes, a sequence
    # containing a single str, boolean or None.

    # Conversion from raw to processed content and vice versa is only done when required.

    # XML child content  encoding attr  Raw content         Processed content    Remark
    # -----------------  -------------  ------------------  -------------------  ---------
    # "string value"                    ("string value",)   ("string value",)    If content is printable, it's a `str`
    # "=00"              "quopri"       ("=00",)            (b"\00",)            Encoded/unprintable content is `bytes`
    # "AA=="             "base64"       ("AA==",)           (b"\00",)
    # <true/>                           (True,)             (True,)
    # <false/>                          (False,)            (False,)
    # <none/>                           (None,)             (None,)
    #
    # value attr  type attr  encoding attr  Raw content         Processed content
    # ----------  ---------  -------------  ------------------  ------------------------------
    # "string"    "string"                  (b"string",)        ("string",)
    # "1"         "int"                     (1,)                (1,)
    # "1.0"       "float"                   (1.0,)              (1.0,)
    #
    # Having both the value attribute set and child content is an unsupported. If XML documents contain this, the
    # `value` attribute is used and the child content is ignored during conversion to processed content.

    _raw_content: typing.Optional[typing.Sequence[RawType]] = None  # Raw unprocessed content
    _processed_value: typing.Optional[typing.Sequence[PT]] = None  # Processed content
    _content_type: typing.Optional[str] = None  # The child content

    @property
    def value(self) -> PT:
        """ `value` attribute: The content.

        Setting `value` to `None` will generate a node with a <none/> tag. Set value to `NO_CONTENT` to
        create an empty content node.

        Raises :py:exc:`NoContent` (a subclass of `ValueError`) if no content was set instead of returning `NO_CONTENT`,
        Raises :py:exc:`FileContent` (also a subclass of `ValueError`') if the node refers to an external file.
        """
        assert self._content_set, "Content not set"
        value = self._process_value()[0]
        if value is NO_CONTENT:
            raise NoContent

        return value

    @value.setter
    def value(self, value: PT):
        assert not self._content_set, "Immutable attribute `value`"

        if not (value is None or value is NO_CONTENT or isinstance(value, self.VALID_PROCESSED_TYPES)):
            raise TypeError(f"Invalid type {type(value)} for attribute `value`, expected one of {self.VALID_PROCESSED_TYPES}")

        if not self.HAS_ENCODING and isinstance(value, str) and not is_printable(value):
            raise ValueError("This content cannot be encoded")

        self._value = None
        self._processed_value = None if value is NO_CONTENT else (value,)
        self._raw_content = None
        self._content_set = True

    def _set_type(self, type_: typing.Optional[str]):
        assert not self._type_set, "Immutable attribute `type`"
        assert type_ is None or isinstance(type_, str)

        self._type = type_
        self._type_set = True

    def _create_content(self: ET, *, name: str = None, value: PT = NO_CONTENT) -> ET:
        """ Set content attributes directly

        :param name: name attribute
        :param value: value attribute
        """
        self.name = name
        self.value = value
        return self

    def _join_name(self, parts: typing.Iterable[typing.Union[str, PurePosixPath]]) -> str:
        return '.'.join(str(part) for part in parts)

    def _create_content_from_node(self: ET, node: CT, direct_parent: PCT, ref_parent: typing.Optional[PCT], *,
                                  args: BundleFactoryArguments) -> ET:
        """ Set the attributes from the XML dom node

        Child content is saved as-is and processing is postponed until the value or type properties are accessed

        :param node: the node to copy the attributes from
        :param direct_parent: the node's direct parent
        :param ref_parent: the node's ref-parent, the predecessor to which the 'ref' attribute refers
        """
        assert not self._content_set and not self._type_set, "Content already set"

        name_parts = self._get_attr_base_parts('name', node, direct_parent, ref_parent)
        # src_parts = self._get_attr_base_parts(
        #     'src', node, direct_parent, ref_parent,
        #     lambda src: src[5:] if src.lower().startswith('file:') else src
        # )

        self._name = self._join_name(name_parts) if name_parts else None
        # self._src = PurePosixPath(*src_parts) if src_parts else None
        self._value = getattr(node, 'value', None)

        raw_content: typing.MutableSequence[RawType] = deque()
        for item in node.any_element:
            if isinstance(item, str):
                raw_content.append(item)
            else:
                # TODO 'list' and 'tuple' elements
                if item.qname == true_qname:
                    raw_content.append(True)
                elif item.qname == false_qname:
                    raw_content.append(False)
                elif item.qname == none_qname:
                    raw_content.append(None)

        self._raw_content = tuple(raw_content) if raw_content else None
        self._processed_value = None
        self._content_type = None

        self._content_set = True
        self._type_set = True
        return self

    def _process_value(self) -> typing.Tuple[PT, typing.Optional[str]]:
        """ Get the processed value and content_type by decoding `value` attribute or raw content.
        If there is no content raises :py:exc:`NoContent`

        Returns the processed value and the type
        """
        assert self._content_set, "No content provided"
        # assert self._src is None

        if self._processed_value is None:
            if self._value is not None:
                typename = self._type
                typename = ALTERNATE_VALUE_TYPES.get(typename, typename)

                if typename and typename not in VALUE_TYPE_MAP:
                    warnings.warn(f"Invalid type {typename!r} for option {self.name!r} ignored")

                datatype = VALUE_TYPE_MAP.get(typename, str)
                try:
                    self._processed_value = (datatype(self._value),)
                except ValueError:
                    self._processed_value = (self._value,)

                self._content_type = None

            elif self._raw_content is not None or self._encoding is not None:
                content: typing.MutableSequence[PT] = deque()
                content_text: str = ''
                if self._raw_content is not None:
                    has_text_content: bool = False
                    for item in self._raw_content:
                        if isinstance(item, str):
                            content_text += item
                            has_text_content |= bool(item.lstrip())

                        elif has_text_content:
                            warnings.warn("Mixed content of strings and elements not supported")

                        else:
                            content.append(item)
                else:
                    # Empty content is considered to be an empty string
                    has_text_content: bool = True

                if has_text_content:
                    if self._encoding:
                        decoded = decode_data(content_text, self._encoding)
                        self._processed_value = (decoded,)
                    else:
                        self._processed_value = (content_text,)
                else:
                    self._processed_value = (content[0],)

                self._content_type = self._type

            else:
                # No content at all
                self._processed_value = tuple()
                self._content_type = None

        return self._processed_value[0] if self._processed_value else NO_CONTENT, self._content_type

    def _create_raw_content(self):
        """ Update __raw_content, __encoding, _type and _value attributes based on __processed_value and __content_type
        """
        # assert self._src is None

        if self._processed_value is not None and self._raw_content is None and self._value is None:
            value = self._processed_value[0] if self._processed_value else None
            if not self._processed_value:
                # Empty tuple, indicates empty node
                self._raw_content = tuple()
                self._encoding = None
                self._value = None
                self._type = None
                if self._content_type:
                    warnings.warn('"type" attribute cannot be used for empty content nodes')

            elif value is None or isinstance(value, bool):
                # Encoded using child elements <none/>, <true/> or <false/>
                self._raw_content = (value,)
                self._encoding = None
                self._value = None
                self._type = None

                if self._content_type:
                    warnings.warn('"type" attribute cannot be combined with None or boolean values')

            elif self._content_type is not None or isinstance(value, bytes) or (
                    isinstance(value, str) and (len(value) > self.MAX_VALUE_LENGTH or not is_printable(value))
            ):
                if self.HAS_ENCODING:
                    # Text content that needs to be encoded as child content
                    encoded, encoding = encode_data(value)
                elif isinstance(value, bytes):
                    encoded, encoding = value.decode('utf-8'), None
                else:
                    encoded, encoding = value, None

                self._raw_content = (encoded,)
                self._encoding = encoding
                self._value = None
                self._type = self._content_type

            else:
                # Something that can be stored in the value attribute
                self._raw_content = None
                self._encoding = None
                self._value = str(value)

                # TODO 'list' and 'tuple' elements
                if isinstance(value, int):
                    self._type = 'integer'
                elif isinstance(value, (float, Decimal)):
                    self._type = 'float'
                else:  # 'string' is default
                    self._type = None

                if self._content_type:
                    warnings.warn('"type" attribute cannot be used for numeric values')

    def __construct_raw_node(self, item: typing.Any) -> typing.Union[AnyElement, str]:
        if isinstance(item, bool):
            return AnyElement(qname=true_qname if item else false_qname)
        elif item is None:
            return AnyElement(qname=none_qname)
        elif isinstance(item, str):
            return item

        raise ValueError("Unable to convert convert element {}".format(item))

    # noinspection PyProtectedMember
    def _construct_content(self, node: CT, *, args: BundleConstructionArguments) -> CT:
        """ Update the attributes of an XML dom node

        :param node: The node to update
        :return: node
        """
        self._create_raw_content()

        if self._name is not None:
            setattr(node, 'name', str(self._name))

        # if self._src is not None:
        #     setattr(node, 'src', str(self._src))

        if self._encoding is not None:
            setattr(node, 'encoding', self._encoding)

        if self._value is not None:
            setattr(node, 'value', self._value)

        if self._type is not None:
            setattr(node, 'type', self._type)

        if self._raw_content:
            node.any_element = [
                self.__construct_raw_node(item)
                for item in self._raw_content
            ]

        return node

    def has_inline_content(self) -> bool:
        """ Returns True if element has inline content, without processing the content
        """
        assert self._content_set, "No content provided"
        return (
            self._encoding is not None or self._value is not None
            or self._raw_content is not None or self._processed_value is not None
        )

    def has_inline_text_content(self) -> bool:
        """ Returns True if self.value would return text content
        (either bytes or str), without converting the content.
        """
        assert self._content_set, "No content provided"

        if self._encoding is not None or (
            self._processed_value and len(self._processed_value) == 1
                and isinstance(self._processed_value[0], (bytes, str))
        ):
            return True

        elif self._raw_content is not None:
            for item in self._raw_content:
                if isinstance(item, str):
                    if item.strip() != '':
                        return True
                else:
                    return False

        elif self._value is not None:
            return self._type is None or self._type == 'string'

        return False

    # noinspection PyMethodMayBeStatic
    def has_attachment_content(self) -> bool:
        """ Returns True if this element has an existing attachment  """
        return False

    def has_text_content(self) -> bool:
        """ Returns True if the element has text content """
        return self.has_inline_text_content() or self.has_attachment_content()

    def _get_bytes_content(self) -> bytes:
        if self.has_inline_text_content():
            value = self._process_value()[0]
            return value.encode('utf-8') if isinstance(value, str) else value

        raise ValueError


class ContentBasicElement(typing.Generic[CT, PCT], ContentElementBase[ContentBasicProcessedType, CT, PCT], ABC):
    VALID_PROCESSED_TYPES: typing.ClassVar = (str, bool)
    HAS_ENCODING = False


class ContentFullElement(typing.Generic[CT, PCT], ContentElementBase[ContentFullProcessedType, CT, PCT], ABC):
    """ A :py:class:`~momotor.bundles.elements.content.ContentElement` variant exposing the type property
    """
    VALID_PROCESSED_TYPES: typing.ClassVar = ContentBasicElement.VALID_PROCESSED_TYPES + (bytes, int, float, Decimal)
    HAS_ENCODING = True

    @property
    def type(self) -> typing.Optional[str]:
        """ The `type` attribute. Indicates the type of the `value` attribute: string, integer or float """
        return self._process_value()[1]

    @type.setter
    def type(self, type_: typing.Optional[str]):
        super()._set_type(type_)

    @property
    def encoding(self) -> typing.Optional[str]:
        """ `encoding` attribute: read-only, the encoding is automatically determined from the value """
        self._create_raw_content()
        return self._encoding

    # noinspection PyShadowingBuiltins,PyMethodOverriding
    def _create_content(self: ET, *,
                        name: str,
                        value: ContentBasicProcessedType = NO_CONTENT,
                        type: str = None) -> ET:
        self.name = name
        self.value = value
        self.type = type
        return self

    def _create_content_from_node(self: ET, node: CT, direct_parent: PCT, ref_parent: typing.Optional[PCT], *,
                                  args: BundleFactoryArguments) -> ET:
        """ Set the attributes from the XML dom node

        Child content is saved as-is and processing is postponed until the value or type properties are accessed

        :param node: the node to copy the attributes from
        :param direct_parent: the node's direct parent
        :param ref_parent: the node's ref-parent, the predecessor to which the 'ref' attribute refers
        """
        super()._create_content_from_node(node, direct_parent, ref_parent, args=args)

        self._type = getattr(node, 'type', None)
        self._encoding = getattr(node, 'encoding', None)

        return self


CSE = typing.TypeVar('CSE', bound="ContentSrcElement")


class ContentAttachmentElement(NamePathMixin, SrcAttachmentMixin, ContentFullElement[CT, PCT], ABC):
    """ A :py:class:`~momotor.bundles.elements.content.ContentElement` variant exposing the type and src properties
    """
    @property
    def type(self) -> typing.Optional[str]:
        """ The `type` attribute. """
        if self.has_attachment_content():
            return self._type
        else:
            return self._process_value()[1]

    @type.setter
    def type(self, type_: typing.Optional[str]):
        super()._set_type(type_)

    def _create_raw_content(self):
        if self.has_attachment_content():
            self._type = self._content_type
            self._raw_content = None
            self._encoding = None
        else:
            return super()._create_raw_content()

    def _process_value(self) -> typing.Tuple[PT, typing.Optional[str]]:
        """ Get the processed value and content_type by decoding `value` attribute or raw content.

        :returns: the processed value and the type
        :raises NoContent: if there is no content (empty XML node)
        :raises AttachmentContent: if the content is in an attachment (`src` attribute set)
        """
        if self.has_attachment_content():
            raise AttachmentContent

        return super()._process_value()

    # noinspection PyShadowingBuiltins
    def _create_content(self: ET, *,
                        name: typing.Union[str, PurePath] = None,
                        src: typing.Union[AttachmentSrc, PurePath] = None,
                        value: ContentBasicProcessedType = NO_CONTENT,
                        type: str = None) -> ET:

        assert not self._content_set and not self._type_set, "Content already set"
        assert value is NO_CONTENT or src is None, "Cannot set both `value` and `src`"

        self.name = name
        self.src = src
        self.value = value
        self.type = type

        return self

    def _create_content_from_node(self: ET, node: CT, direct_parent: PCT, ref_parent: typing.Optional[PCT], *,
                                  args: BundleFactoryArguments) -> ET:
        """ Set the attributes from the XML dom node

        Child content is saved as-is and processing is postponed until the value or type properties are accessed

        :param node: the node to copy the attributes from
        :param direct_parent: the node's direct parent
        :param ref_parent: the node's ref-parent, the predecessor to which the 'ref' attribute refers
        """
        super()._create_content_from_node(node, direct_parent, ref_parent, args=args)

        src_set = False
        if not self.has_inline_content():
            # Collect `src` path.
            parts = deque()

            value = node.src
            if value is None:
                value = node.name
            elif value.lower().startswith('file:'):
                value = value[5:]

            if value is not None:
                parent_value = getattr(direct_parent, 'basesrc', None)
                if parent_value is not None:
                    parts.append(parent_value)

                if ref_parent:
                    ref_value = getattr(ref_parent, 'basesrc', None)
                    if ref_value is not None:
                        parts.append(ref_value)

                parts.append(value)

            if parts:
                self.src = AttachmentSrc(PurePosixPath(*parts), self.bundle, validate=args.validate_signature)
                src_set = True

        if not src_set:
            self.src = None

        return self

    # noinspection PyProtectedMember,PyMethodOverriding
    def _construct_content(self, node: CT, basesrc: PurePosixPath, *, args: BundleConstructionArguments) -> CT:
        """ Update the attributes of an XML dom node

        :param node: The node to update
        :return: node
        """
        super()._construct_content(node, args=args)

        if self.has_attachment_content():
            export_src = self._export_path(basesrc / self.name)
            src_attr = str(export_src.relative_to(basesrc))
            if src_attr != str(self.name) or args.legacy:
                setattr(node, 'src', src_attr)

        return node

    # Override AttachmentMixin functions to add support for inline content

    def has_writable_content(self):
        return super().has_writable_content() or self.has_inline_text_content()

    def file_size(self, path: typing.Union[str, PurePosixPath] = None) -> typing.Optional[int]:
        """ Get file size for the content.

        :return: The file size
        """
        if self.has_inline_text_content():
            if path is not None:
                raise FileNotFoundError

            return len(self.value)

        return SrcAttachmentMixin.file_size(self, path)

    def is_dir(self, path: typing.Union[str, PurePosixPath] = None) -> bool:
        return not self.has_inline_text_content() and SrcAttachmentMixin.is_dir(self, path)

    def open(self, path: typing.Union[str, PurePosixPath] = None) -> typing.BinaryIO:
        if self.has_inline_text_content():
            if path:
                raise FileNotFoundError

            return BytesIO(self._get_bytes_content())

        return SrcAttachmentMixin.open(self, path)

    def read(self, path: typing.Union[str, PurePosixPath] = None) -> bytes:
        if self.has_inline_text_content():
            if path:
                raise FileNotFoundError

            return self._get_bytes_content()

        return SrcAttachmentMixin.read(self, path)

    def _dest_name(self) -> typing.Optional[PurePath]:
        return self.name or SrcAttachmentMixin._dest_name(self)

    def _copy_file(self, dest_path: Path):
        if self.has_inline_text_content():
            with dest_path.open('wb') as writer:
                writer.write(self._get_bytes_content())
        else:
            SrcAttachmentMixin._copy_file(self, dest_path)


# Extend the docstrings with the generic documentation of Element
if Element.__doc__:
    if ContentBasicElement.__doc__:
        ContentBasicElement.__doc__ += "\n".join(Element.__doc__.split("\n")[1:])

    if ContentFullElement.__doc__:
        ContentFullElement.__doc__ += "\n".join(Element.__doc__.split("\n")[1:])

    if ContentAttachmentElement.__doc__:
        ContentAttachmentElement.__doc__ += "\n".join(Element.__doc__.split("\n")[1:])
