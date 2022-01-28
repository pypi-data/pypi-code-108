from dataclasses import dataclass, field
from enum import Enum

from .localized_string import LocalizedString


class FormattedStringFormat(str, Enum):
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    TEXT_MARKDOWN = "text/markdown"
    APPL_DOCBOOK_XML = "application/docbook+xml"
    APPL_TEI_XML = "application/tei+xml"
    APPL_X_ASCIIDOC = "text/x-asciidoc"
    APPL_X_ISODOC_XML = "application/x-isodoc+xml"


@dataclass(frozen=True)
class FormattedString(LocalizedString):
    format: str = field(default=FormattedStringFormat.TEXT_PLAIN.value)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.format, FormattedStringFormat):
            object.__setattr__(self, "format", self.format.value)

    def to_xml(self, parent):
        if self.format:
            parent.attrib["format"] = self.format
        return super().to_xml(parent)

    def to_asciibib(self, prefix="", count=1, has_attrs=False):
        has_attrs = has_attrs or self.format
        pref = f"{prefix}." if prefix else prefix
        out = [super().to_asciibib(prefix, count, has_attrs)]
        if self.format:
            out.append(f"{pref}format:: {self.format}")
        return "\n".join(out)
